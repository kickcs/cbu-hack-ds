"""What ingestion has to say about a file besides its numbers.

A submitted file is rarely perfectly formed, and the two failure modes need different
answers: a file that cannot be parsed at all stops the job, a file that is merely dirty --
a few unparseable amounts, an unknown indicator name, a bank with too few loans -- must
still be audited, with the damage stated. `Issue` carries both, separated by `level`:

  ERROR    the file (or the submission) cannot be audited; the job fails with this text;
  WARNING  the audit ran, but this is what it had to ignore or assume.

Messages are shown verbatim to the auditor in the dashboard, next to the report they belong
to, so they read as sentences and count their own nouns. `count` holds the tally behind a
message that has one, for callers that need the number rather than the sentence.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class Issue(BaseModel):
    """One remark about a submitted file, addressed to the auditor reading the report."""

    level: Severity
    code: str = Field(description="Stable machine key, e.g. `amounts_dropped`.")
    message: str = Field(description="Sentence shown in the dashboard.")
    file: str | None = Field(default=None, description="File the issue belongs to.")
    count: int | None = Field(default=None, description="The tally the message states, when it has one.")


def tally(n: int, one: str, many: str) -> str:
    """`1 row is` / `4 rows are` — a count with its noun in the right number."""
    return f"{n} {one if n == 1 else many}"


def error(code: str, message: str, *, file: str | None = None, count: int | None = None) -> Issue:
    return Issue(level=Severity.ERROR, code=code, message=message, file=file, count=count)


def warning(code: str, message: str, *, file: str | None = None, count: int | None = None) -> Issue:
    return Issue(level=Severity.WARNING, code=code, message=message, file=file, count=count)


def has_errors(issues: list[Issue]) -> bool:
    return any(i.level is Severity.ERROR for i in issues)


def first_error(issues: list[Issue]) -> Issue | None:
    return next((i for i in issues if i.level is Severity.ERROR), None)
