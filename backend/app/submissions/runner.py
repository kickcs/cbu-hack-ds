"""Auditing one submission, in isolation from the shared dataset.

The audit itself is unchanged -- same Benford test, same detectors, same thresholds. What
differs is the input: a directory holding only what this bank uploaded, which may cover one
dataset instead of three. So the run has to answer two questions the shared pipeline never
faces: is there anything auditable here at all, and which tests must be reported as *not
run* rather than as passed.

`SubmissionError` carries the auditor-facing reason a submission cannot be audited; the
worker turns it into the `FAILED` status verbatim.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from ..audit import BENFORD_REASON, audit_all, rank_banks
from ..detectors import DETECTORS, AuditContext, runnable
from ..domain import BankAudit
from ..ingest import ROLE_LABELS, Issue, Role, load_dataset
from .model import SubmissionFile

log = logging.getLogger(__name__)


class SubmissionError(RuntimeError):
    """The submission cannot be audited; the message is shown to the auditor."""


@dataclass
class SubmissionRun:
    """Everything one submission produced, ready to be written back to its row."""

    files: list[SubmissionFile] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    results: list[BankAudit] = field(default_factory=list)


def audit_submission(directory: Path, files: list[SubmissionFile]) -> SubmissionRun:
    """Ingest the submission directory and audit whatever it turned out to contain."""
    loaded = load_dataset(directory)
    if not loaded.roles:
        raise SubmissionError(_nothing_usable(loaded.issues))

    ctx = AuditContext(register=loaded.register, normativ=loaded.normativ, report=loaded.report)
    active = {d.name for d in runnable(DETECTORS, ctx)}
    skipped = [d.name for d in DETECTORS if d.name not in active]
    if Role.REGISTER not in loaded.roles:
        skipped.append(BENFORD_REASON)

    results = rank_banks(audit_all(loaded.register, loaded.normativ, loaded.report))
    if not results:
        raise SubmissionError("No bank could be identified in the uploaded files.")

    log.info(
        "submission: %s banks, %s suspicious, skipped=%s",
        len(results),
        sum(r.suspicious for r in results),
        skipped or "-",
    )
    return SubmissionRun(
        files=_enrich(files, loaded),
        issues=loaded.issues,
        skipped=skipped,
        results=results,
    )


def _enrich(files: list[SubmissionFile], loaded) -> list[SubmissionFile]:
    """Fill in what ingestion learned about each stored file: its role and its row count."""
    by_name = {f.name: f for f in loaded.files}
    enriched = []
    for stored in files:
        found = by_name.get(stored.name)
        enriched.append(
            stored.model_copy(
                update={
                    "role": found.role if found else Role.UNKNOWN,
                    "role_label": found.role_label if found else ROLE_LABELS[Role.UNKNOWN],
                    "rows": found.rows if found else 0,
                }
            )
        )
    return enriched


def _nothing_usable(issues: list[Issue]) -> str:
    """Turn the ingestion issues into one sentence explaining the rejection."""
    errors = [i for i in issues if i.level == "error"]
    names = ", ".join(sorted({i.file for i in errors if i.file}))
    head = "Nothing in this filing is a loan register, a set of prudential ratios or a report"
    head = f"{head} ({names})." if names else f"{head}."
    # A file that could not even be read failed differently, so it says so as well.
    unreadable = [i for i in errors if i.code != "unrecognized"]
    return " ".join([head, *(f"{i.file}: {i.message}" for i in unreadable[:2])]).strip()
