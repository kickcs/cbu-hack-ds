"""Shape of the loan register: how to find the bank column and one bank's amounts.

The register arrives as a flat CSV, one row per loan, with the bank name in the first
column. Its exact header is not fixed (the day-2 dataset may rename it), so every reader
of the register goes through here instead of hardcoding a column name or `columns[0]`.
"""
from __future__ import annotations

import pandas as pd

AMOUNT_COLUMN = "summa"


def bank_column(register: pd.DataFrame) -> str:
    """Name of the column holding the bank a loan belongs to."""
    return register.columns[0]


def bank_names(register: pd.DataFrame) -> list[str]:
    """Every bank present in the register, sorted case-insensitively."""
    return sorted((str(b) for b in register[bank_column(register)].unique()), key=str.lower)


def loan_amounts(register: pd.DataFrame, bank: str, *, exact: bool = True) -> pd.Series:
    """Loan amounts issued by one bank.

    `exact=False` matches the bank name case-insensitively -- used on API routes, where
    the name arrives from the URL and its casing cannot be trusted.
    """
    names = register[bank_column(register)]
    mask = names == bank if exact else names.astype(str).str.lower() == bank.lower()
    return register[mask][AMOUNT_COLUMN]
