"""Multi-format ingestion: CSV / XLSX / XML bank reports -> canonical indicator model.

Canonical model: records (bank, period, indicator, tip, summa) where `indicator` is
one of the canonical keys in `indicators.py`. Raw source files are preserved unchanged
(bitemporal requirement: `period` (отчётный) and `received_at` (подача) are kept
separate, see repository.py).

Split of responsibilities:
- `readers.py`    -- one reader per file format, all producing the same records;
- `indicators.py` -- raw indicator labels -> canonical keys (synonyms + fuzzy fallback);
- `register.py`   -- shape of the loan register (which column holds the bank);
- this module     -- loading a whole dataset directory.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .indicators import CANONICAL_INDICATORS, map_indicator, unknown_indicator_count
from .readers import READERS
from .register import AMOUNT_COLUMN, bank_column, bank_names, loan_amounts

__all__ = [
    "AMOUNT_COLUMN",
    "CANONICAL_INDICATORS",
    "bank_column",
    "bank_names",
    "load_aggregate_reports",
    "load_credit_register",
    "load_normativ",
    "loan_amounts",
    "map_indicator",
    "unknown_indicator_count",
]


def load_aggregate_reports(reports_dir: str | Path) -> pd.DataFrame:
    """Load csv/xlsx/xml report files from a directory into the canonical model."""
    reports_dir = Path(reports_dir)
    records: list[dict] = []
    for p in sorted(reports_dir.rglob("*")):
        if not p.is_file() or p.name.startswith("~"):
            continue
        reader = READERS.get(p.suffix.lower())
        if reader is not None:
            records.extend(reader(p))
    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"no report files found in {reports_dir}")
    return df


def load_credit_register(path: str | Path) -> pd.DataFrame:
    """Load the loan register (canonical form, one row per loan)."""
    return pd.read_csv(path)


def load_normativ(path: str | Path) -> pd.DataFrame:
    """Load regulatory ratios (K1/LCR/K3) with their thresholds."""
    return pd.read_csv(path)
