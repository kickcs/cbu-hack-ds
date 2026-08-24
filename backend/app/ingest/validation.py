"""Everything that can be wrong with a submitted file, checked in one place.

The audit is a statistical argument, and every one of these checks exists because ignoring
it would corrupt that argument silently rather than loudly:

- an unreadable amount coerced to zero would move a first digit into the Benford histogram;
- a bank whose name is blank would split its loans off into a phantom bank with a tiny,
  automatically "suspicious" sample;
- a duplicated register row inflates n, which narrows the very sampling noise MIN_SAMPLE
  exists to respect;
- a report period that failed to parse silently drops a bank out of the growth detectors.

So the rule here is: never repair data quietly. Either the file is rejected with a reason
(`Severity.ERROR`), or it is audited with the damage listed (`Severity.WARNING`) next to the
result. `validate_*` returns the cleaned frame together with what had to be said about it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from ..sampling import MIN_SAMPLE, is_sample_sufficient
from .classify import NORMATIV_COLUMNS, PERIOD_COLUMNS, Role
from .issues import Issue, error, tally, warning
from .register import amount_column, bank_column
from .tabular import resolve_column, to_amounts

ALLOWED_SUFFIXES: frozenset[str] = frozenset({".csv", ".xlsx", ".xml"})
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_FILES = 20

_UNSAFE_NAME = re.compile(r"[^\w.\- ]+", re.UNICODE)


def safe_name(name: str) -> str:
    """A filename that cannot escape its own directory.

    Only the basename survives, and everything outside word characters, dots, dashes and
    spaces is replaced -- an upload named `../../etc/passwd` is stored as `passwd`.
    """
    base = Path(str(name)).name.strip() or "file"
    cleaned = _UNSAFE_NAME.sub("_", base).lstrip(".") or "file"
    return cleaned[:120]


def check_upload(name: str, size: int) -> list[Issue]:
    """Reject a file before it is written to disk: wrong format, empty, or oversized."""
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        return [
            error(
                "unsupported_format",
                f"{suffix or 'A file with no extension'} is not supported — upload CSV, XLSX or XML.",
                file=name,
            )
        ]
    if size <= 0:
        return [error("empty_file", "The file is empty.", file=name)]
    if size > MAX_FILE_BYTES:
        limit = MAX_FILE_BYTES // (1024 * 1024)
        return [
            error("file_too_large", f"The file is over {limit} MB — split the export and upload it in parts.", file=name)
        ]
    return []


def validate_register(frame: pd.DataFrame, file: str) -> tuple[pd.DataFrame, list[Issue]]:
    """Clean a loan register and report what had to be dropped or assumed."""
    issues: list[Issue] = []
    bank_col, amount_col = bank_column(frame), amount_column(frame)

    if amount_col not in frame.columns:
        return frame, [error("no_amount_column", "The register has no loan amount column.", file=file)]

    frame = frame.copy()
    amounts, unreadable = to_amounts(frame[amount_col])
    frame[amount_col] = amounts
    if unreadable:
        issues.append(
            warning(
                "amounts_unreadable",
                f"{tally(unreadable, 'amount is', 'amounts are')} not readable as numbers — "
                "those rows are left out of the test.",
                file=file,
                count=unreadable,
            )
        )

    blank_banks = int(frame[bank_col].isna().sum() + (frame[bank_col].astype(str).str.strip() == "").sum())
    if blank_banks:
        issues.append(
            warning(
                "bank_missing",
                f"{tally(blank_banks, 'row names', 'rows name')} no bank — dropped, or they "
                "would form a phantom bank of their own.",
                file=file,
                count=blank_banks,
            )
        )
        frame = frame[frame[bank_col].notna() & (frame[bank_col].astype(str).str.strip() != "")]

    nonpositive = int((frame[amount_col] <= 0).sum())
    if nonpositive:
        issues.append(
            warning(
                "amounts_nonpositive",
                f"{tally(nonpositive, 'amount is', 'amounts are')} zero or negative — there is "
                "no leading significant digit to read.",
                file=file,
                count=nonpositive,
            )
        )

    duplicates = int(frame.duplicated().sum())
    if duplicates:
        issues.append(
            warning(
                "duplicate_rows",
                f"{tally(duplicates, 'row is an exact duplicate', 'rows are exact duplicates')} — "
                "repeats overstate the sample size.",
                file=file,
                count=duplicates,
            )
        )

    frame = frame.dropna(subset=[amount_col])
    if frame.empty:
        return frame, [*issues, error("register_empty", "No usable rows are left in the register.", file=file)]

    small = [
        str(bank)
        for bank, rows in frame.groupby(bank_col)
        if not is_sample_sufficient(int(len(rows)))
    ]
    if small:
        issues.append(
            warning(
                "sample_insufficient",
                f"{tally(len(small), 'bank holds', 'banks hold')} fewer than {MIN_SAMPLE} loans "
                f"({', '.join(small[:5])}{'…' if len(small) > 5 else ''}). "
                f"{'Its' if len(small) == 1 else 'Their'} Benford reading is withheld "
                "rather than reported.",
                file=file,
                count=len(small),
            )
        )
    return frame, issues


def validate_normativ(frame: pd.DataFrame, file: str) -> tuple[pd.DataFrame, list[Issue]]:
    """Check that the regulatory ratios carry both the readings and their limits."""
    issues: list[Issue] = []
    missing = [c for c in NORMATIV_COLUMNS if resolve_column(frame, (c,)) is None]
    if len(missing) == len(NORMATIV_COLUMNS):
        return frame, [error("normativ_columns", "The file carries none of the K1, LCR or K3 ratios.", file=file)]
    if missing:
        issues.append(
            warning(
                "normativ_partial",
                f"Missing columns: {', '.join(missing)} — the tests that read them are skipped.",
                file=file,
                count=len(missing),
            )
        )
    if resolve_column(frame, PERIOD_COLUMNS) is None:
        issues.append(
            warning("normativ_no_period", "The ratios carry no period, so their movement is not read.", file=file)
        )
    return frame, issues


def validate_report(frame: pd.DataFrame, file: str, unknown_names: int = 0) -> list[Issue]:
    """Check the canonical aggregate report after ingestion."""
    issues: list[Issue] = []
    if frame.empty:
        return [error("report_empty", "No indicator could be read out of the reports.", file=file)]

    if unknown_names:
        issues.append(
            warning(
                "indicators_unknown",
                f"{tally(unknown_names, 'indicator name matches', 'indicator names match')} nothing "
                "in the reference list — those lines are skipped.",
                file=file,
                count=unknown_names,
            )
        )

    blank_period = int((frame["period"].astype(str).str.strip() == "").sum())
    if blank_period:
        issues.append(
            warning(
                "period_missing",
                f"{tally(blank_period, 'line carries', 'lines carry')} no reporting period — "
                "the movement tests cannot see them.",
                file=file,
                count=blank_period,
            )
        )

    duplicates = int(frame.duplicated(subset=["bank", "period", "indicator"]).sum())
    if duplicates:
        issues.append(
            warning(
                "report_duplicates",
                f"{tally(duplicates, 'repeat', 'repeats')} of bank + period + indicator — "
                "the last value filed was used.",
                file=file,
                count=duplicates,
            )
        )

    periods = frame.groupby("bank")["period"].nunique()
    thin = [str(b) for b, n in periods.items() if n < 2]
    if thin:
        issues.append(
            warning(
                "single_period",
                f"{tally(len(thin), 'bank filed', 'banks filed')} a single period — the growth "
                "and window-dressing tests need at least two.",
                file=file,
                count=len(thin),
            )
        )
    return issues


def missing_dataset_note(role: Role) -> Issue:
    """Say plainly which tests a submission cannot reach, instead of showing them as passed."""
    texts = {
        Role.REGISTER: "No loan register in this filing — Benford's law and the last-digit test did not run.",
        Role.NORMATIV: "No prudential ratios in this filing — the K1 limit test did not run.",
        Role.REPORT: "No aggregate report in this filing — the rounding, footing and growth tests did not run.",
    }
    return warning(f"no_{role.value}", texts[role])
