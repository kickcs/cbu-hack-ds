"""Turning a directory of submitted files into the three datasets the audit needs.

`load_aggregate_reports` and friends assume the sample's layout -- fixed filenames, one
role per known path. A submission uploaded through the dashboard has neither: it is a
handful of files whose roles have to be read off their contents (`classify.py`), whose
defects have to be reported rather than repaired (`validation.py`), and which may cover
only part of the picture. A register alone is a valid submission; so is a single XLSX.

What comes back is deliberately partial: the frames that could be built, the files that
went into each, and everything that had to be said about them. Deciding which tests can
run on that is the audit's job, not ingestion's -- see `detectors.runnable`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .classify import ROLE_LABELS, Role, classify_file
from .indicators import unknown_indicator_names
from .issues import Issue, error, warning
from .readers import READERS
from .tabular import read_csv_any
from .validation import (
    ALLOWED_SUFFIXES,
    missing_dataset_note,
    validate_normativ,
    validate_register,
    validate_report,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadedFile:
    """One submitted file after ingestion: what it turned out to be, and how much of it."""

    name: str
    role: Role
    role_label: str
    rows: int


@dataclass
class LoadedDataset:
    """The datasets a submission yielded, with the files and the remarks behind them."""

    register: pd.DataFrame | None = None
    normativ: pd.DataFrame | None = None
    report: pd.DataFrame | None = None
    files: list[LoadedFile] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def roles(self) -> set[Role]:
        """Dataset slots actually filled -- what the audit has to work with."""
        return {
            role
            for role, frame in (
                (Role.REGISTER, self.register),
                (Role.NORMATIV, self.normativ),
                (Role.REPORT, self.report),
            )
            if frame is not None and not frame.empty
        }


def load_dataset(directory: str | Path) -> LoadedDataset:
    """Read every file in `directory`, classify it, validate it, and stack it by role."""
    from . import iter_data_files  # noqa: PLC0415 -- facade module, imported lazily

    loaded = LoadedDataset()
    registers: list[pd.DataFrame] = []
    normativs: list[pd.DataFrame] = []
    records: list[dict] = []
    # The unmapped-indicator set is process-wide; the difference across this load is what
    # this submission failed to map.
    unknown_before = unknown_indicator_names()

    for path in iter_data_files(directory):
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            loaded.issues.append(
                error("unsupported_format", f"{path.suffix or 'This format'} is not a supported format.", file=path.name)
            )
            continue
        role = classify_file(path)
        try:
            rows = _read_one(path, role, registers, normativs, records, loaded)
        except Exception as exc:  # noqa: BLE001 -- any parser failure is a finding, not a crash
            log.warning("ingest: %s failed to parse: %s", path.name, exc)
            loaded.issues.append(error("unreadable", f"The file could not be read: {exc}", file=path.name))
            continue
        loaded.files.append(LoadedFile(path.name, role, ROLE_LABELS[role], rows))

    loaded.register = pd.concat(registers, ignore_index=True) if registers else None
    loaded.normativ = pd.concat(normativs, ignore_index=True) if normativs else None
    loaded.report = pd.DataFrame(records) if records else None
    if loaded.report is not None:
        unmapped = len(unknown_indicator_names() - unknown_before)
        loaded.issues.extend(validate_report(loaded.report, "reports", unmapped))

    for missing in (Role.REGISTER, Role.NORMATIV, Role.REPORT):
        if missing not in loaded.roles:
            loaded.issues.append(missing_dataset_note(missing))
    return loaded


def _read_one(
    path: Path,
    role: Role,
    registers: list[pd.DataFrame],
    normativs: list[pd.DataFrame],
    records: list[dict],
    loaded: LoadedDataset,
) -> int:
    """Ingest one file into the accumulator for its role; return the rows it contributed."""
    if role is Role.REGISTER:
        frame, issues = validate_register(read_csv_any(path), path.name)
        loaded.issues.extend(issues)
        if not frame.empty:
            registers.append(frame)
        return int(len(frame))

    if role is Role.NORMATIV:
        frame, issues = validate_normativ(read_csv_any(path), path.name)
        loaded.issues.extend(issues)
        normativs.append(frame)
        return int(len(frame))

    if role is Role.REPORT:
        before = len(records)
        records.extend(READERS[path.suffix.lower()](path))
        rows = len(records) - before
        if rows == 0:
            loaded.issues.append(
                error("no_indicators", "No line matched a known indicator name.", file=path.name)
            )
        if path.suffix.lower() == ".xlsx" and rows:
            bank = {r["bank"] for r in records[before:]}
            loaded.issues.append(
                warning(
                    "bank_from_filename",
                    f"The workbook names no bank, so it was read from the filename: {', '.join(sorted(bank))}.",
                    file=path.name,
                )
            )
        return rows

    loaded.issues.append(
        error(
            "unrecognized",
            "Not a loan register, a set of prudential ratios or an aggregate report.",
            file=path.name,
        )
    )
    return 0
