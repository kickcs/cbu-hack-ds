"""Reading a CSV that was not produced by us, and making its columns usable.

The sample dataset is clean UTF-8 with comma separators. A file uploaded through the
dashboard is not: banks export from Excel, which in this region means Windows-1251 and
semicolons, sometimes a BOM, sometimes thousands separators inside the amounts. None of
that is a data-quality finding -- it is just a file that has to be read before it can be
audited -- so it is handled here, once, rather than in each caller.

Three jobs, in the order a caller needs them:
  `read_csv_any`   bytes on disk -> DataFrame, trying encodings and separators;
  `resolve_column` "the column holding the bank" -> its actual name in this file;
  `to_amounts`     a column of exported text -> floats, plus how much was unreadable.
"""
from __future__ import annotations

import logging
import re
from io import StringIO
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

ENCODINGS: tuple[str, ...] = ("utf-8-sig", "cp1251", "latin-1")
"""Tried in order; `latin-1` never fails, so it is the terminating fallback."""

SEPARATORS: tuple[str, ...] = (",", ";", "\t", "|")

_THOUSANDS = re.compile(r"[\s  ']")
"""Spaces used as digit groupings, including the non-breaking ones Excel emits."""

_NOT_NUMERIC = re.compile(r"[^0-9,.\-+eE]")


def read_csv_any(path: Path) -> pd.DataFrame:
    """Read a CSV whose encoding and separator are unknown.

    Raises `ValueError` with an auditor-facing message when the file is empty or cannot be
    parsed into more than one column under any combination -- that is a file the auditor has
    to fix, not something to guess about.
    """
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError("the file is empty")

    last_error: Exception | None = None
    for encoding in ENCODINGS:
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        for separator in SEPARATORS:
            try:
                frame = pd.read_csv(StringIO(text), sep=separator, dtype=object)
            except Exception as exc:  # noqa: BLE001 -- pandas raises a zoo of parser errors
                last_error = exc
                continue
            if frame.shape[1] > 1:
                frame.columns = [str(c).strip() for c in frame.columns]
                return frame
    raise ValueError(f"the CSV could not be parsed: {last_error or 'no column separator found'}")


def normalize(name: object) -> str:
    """Column name reduced to its comparable core: lowercase, punctuation to spaces."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9а-я]+", " ", str(name).lower())).strip()


def resolve_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    """Find the column a caller means, by exact name then by substring, else None.

    Candidates are given normalized. The substring pass is what absorbs renamings like
    `summa` -> `summa_som` -> `kredit summasi (som)` without a new entry per variant; it
    ignores names shorter than three characters, which match almost anything by accident.
    """
    normalized = {normalize(c): c for c in frame.columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for candidate in candidates:
        for norm, original in normalized.items():
            if candidate in norm or (len(norm) >= 3 and norm in candidate):
                return original
    return None


def parse_amount(value: object) -> float | None:
    """One exported money value as a float, or None when it is not a number.

    Handles the shapes Excel produces -- `1 200 000`, `1 200 000,50`, `1,200,000.50`.
    Returning None rather than 0.0 is the whole point: a zero would carry a first digit
    into the Benford histogram that the bank never reported.
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = _THOUSANDS.sub("", str(value)).strip()
    if not text or _NOT_NUMERIC.search(text):
        return None
    # A lone comma is a decimal point; a comma plus a dot means the comma grouped digits.
    if "," in text:
        text = text.replace(",", "") if "." in text else text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def to_amounts(series: pd.Series) -> tuple[pd.Series, int]:
    """Coerce an exported money column to floats; return the values and how many failed."""
    if series.empty:
        return series.astype(float), 0

    parsed = series.map(parse_amount)
    dropped = int(parsed.isna().sum() - series.isna().sum())
    return pd.to_numeric(parsed, errors="coerce"), max(dropped, 0)
