"""Multi-format ingestion: CSV / XLSX / XML bank reports -> canonical indicator model.

Canonical model: records (bank, period, indicator, tip, summa) where `indicator` is
one of the canonical keys in `indicators.py`. Raw source files are preserved unchanged
(bitemporal requirement: `period` (отчётный) and `received_at` (подача) are kept
separate, see repository.py).

Split of responsibilities:
- `tabular.py`    -- reading a CSV of unknown encoding/separator, resolving its columns;
- `readers.py`    -- one reader per file format, all producing the same records;
- `indicators.py` -- raw indicator labels -> canonical keys (synonyms + fuzzy fallback);
- `register.py`   -- shape of the loan register (which column holds the bank);
- `classify.py`   -- which of the three datasets a submitted file is;
- `validation.py` -- what is wrong with it, as errors and warnings (`issues.py`);
- `dataset.py`    -- an uploaded submission -> the datasets it yielded, partial by design;
- this module     -- loading the dataset directory the service reads from.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .classify import ROLE_LABELS, Role, classify_file, classify_frame
from .dataset import LoadedDataset, LoadedFile, load_dataset
from .indicators import CANONICAL_INDICATORS, map_indicator, unknown_indicator_count
from .issues import Issue, Severity, has_errors
from .readers import READERS
from .register import AMOUNT_COLUMN, amount_column, bank_column, bank_names, loan_amounts
from .tabular import parse_amount, read_csv_any, resolve_column, to_amounts  # noqa: F401 -- facade
from .validation import (
    ALLOWED_SUFFIXES,
    MAX_FILE_BYTES,
    MAX_FILES,
    check_upload,
    missing_dataset_note,
    safe_name,
    validate_normativ,
    validate_register,
    validate_report,
)

__all__ = [
    "ALLOWED_SUFFIXES",
    "AMOUNT_COLUMN",
    "CANONICAL_INDICATORS",
    "MAX_FILES",
    "MAX_FILE_BYTES",
    "ROLE_LABELS",
    "Issue",
    "LoadedDataset",
    "LoadedFile",
    "Role",
    "Severity",
    "amount_column",
    "bank_column",
    "bank_names",
    "check_upload",
    "classify_file",
    "classify_frame",
    "has_errors",
    "iter_data_files",
    "load_aggregate_reports",
    "load_credit_register",
    "load_dataset",
    "load_normativ",
    "loan_amounts",
    "map_indicator",
    "missing_dataset_note",
    "parse_amount",
    "read_csv_any",
    "resolve_column",
    "safe_name",
    "to_amounts",
    "unknown_indicator_count",
    "validate_normativ",
    "validate_register",
    "validate_report",
]


SKIPPED_DIRS: frozenset[str] = frozenset({"node_modules", "__pycache__", "venv", "результат", "natija"})
"""Directories under the dataset root that never hold source data.

Uploads live in a dot-directory (`config.UPLOAD_DIR_NAME`) and are covered by the
dot-prefix rule below -- an uploaded file must stay in its own report and never leak
into the shared dataset.
"""


def iter_data_files(root: str | Path) -> list[Path]:
    """Source files under `root`, in a stable order, with the noise left out.

    Skips dot-directories (uploads, `.git`), the two result directories, dependency trees
    and the `~$…` lock files Excel leaves behind next to an open workbook. Dot and skipped
    directories are pruned at the walk, not merely filtered, so `node_modules` and the like
    are never descended into -- an `rglob` that visits them would dominate the whole scan.
    """
    root = Path(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d not in SKIPPED_DIRS and not d.startswith("~")
        ]
        for name in filenames:
            if name.startswith("~"):
                continue
            path = Path(dirpath) / name
            if path.is_file():
                files.append(path)
    return sorted(files)


def load_aggregate_reports(reports_dir: str | Path) -> pd.DataFrame:
    """Load csv/xlsx/xml report files from a directory into the canonical model."""
    records: list[dict] = []
    for path in iter_data_files(reports_dir):
        reader = READERS.get(path.suffix.lower())
        if reader is not None:
            records.extend(reader(path))
    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"no report files found in {reports_dir}")
    return df


def load_credit_register(path: str | Path) -> pd.DataFrame:
    """Load the loan register (canonical form, one row per loan)."""
    register = read_csv_any(Path(path))
    amounts = amount_column(register)
    if amounts in register.columns:
        register[amounts], _ = to_amounts(register[amounts])
    return register


def load_normativ(path: str | Path) -> pd.DataFrame:
    """Load regulatory ratios (K1/LCR/K3) with their thresholds."""
    normativ = read_csv_any(Path(path))
    for column in normativ.columns:
        if column.lower().startswith(("k1", "k3", "lcr", "chegara")):
            normativ[column], _ = to_amounts(normativ[column])
    return normativ
