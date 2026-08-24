"""What an uploaded report is, from the queue's point of view.

One submission = one set of files = one isolated audit. It moves through four states and
stops in two of them:

    QUEUED -> PROCESSING -> DONE
                         -> FAILED

`DONE` means the audit ran; it does not mean the files were clean. Everything ingestion had
to say is in `issues`, and the tests that could not run for lack of a dataset are in
`skipped` -- a submission of the loan register alone is a perfectly good report that simply
has nothing to say about K1 clustering. Conflating "not tested" with "tested, clean" is the
one reading this model exists to prevent.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from ..domain import BankAudit
from ..ingest import Issue, Role


class SubmissionStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

    @property
    def active(self) -> bool:
        """Still moving: the dashboard keeps polling while any submission is active."""
        return self in (SubmissionStatus.QUEUED, SubmissionStatus.PROCESSING)


class SubmissionFile(BaseModel):
    """One file of a submission, as stored and as understood."""

    name: str
    format: str
    size: int
    sha256: str = Field(description="Digest of the stored bytes -- the evidence trail.")
    role: Role = Role.UNKNOWN
    role_label: str = ""
    rows: int = 0


class Submission(BaseModel):
    """An uploaded report and, once processed, the audit it produced."""

    id: int
    title: str
    status: SubmissionStatus
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    files: list[SubmissionFile] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list, description="Tests that had no input.")
    error: str | None = Field(default=None, description="Why the submission failed, shown verbatim.")
    error_key: str | None = Field(
        default=None,
        description="Stable key the dashboard localizes, when the failure is a known one.",
    )
    error_params: dict[str, str | int] = Field(
        default_factory=dict,
        description="Interpolation values for `error_key`.",
    )
    total_banks: int | None = None
    suspicious_count: int | None = None
    results: list[BankAudit] = Field(default_factory=list, description="Empty in list views.")
