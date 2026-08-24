"""What kind of dataset a submitted file is, decided from its own columns.

The three datasets the audit needs -- the loan register, the regulatory ratios and the
aggregate reports -- arrive under fixed names in the sample (`kredit_reyestri.csv`,
`normativlar.csv`, `csv/ xlsx/ xml/`). A file uploaded through the dashboard carries
whatever name the bank gave it, so its role has to be read off its contents instead.

The order of the checks is the point: a normativ file and a register file both hold a bank
column, and a report file and a register file both hold amounts, so each role is identified
by the marker only it has -- the regulatory limits, the indicator-name column, the loan id.
"""
from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import pandas as pd

from .tabular import read_csv_any, resolve_column

BANK_COLUMNS: tuple[str, ...] = ("bank", "bank nomi", "bank name", "банк", "наименование банка")
AMOUNT_COLUMNS: tuple[str, ...] = ("summa", "summa som", "kredit summasi", "amount", "сумма")
LOAN_ID_COLUMNS: tuple[str, ...] = ("kredit id", "loan id", "shartnoma", "id kredita")
PERIOD_COLUMNS: tuple[str, ...] = ("oy", "hisobot oyi", "davr", "period", "месяц", "период")
INDICATOR_COLUMNS: tuple[str, ...] = ("korsatkich nomi", "korsatkich", "показатель", "indicator")
NORMATIV_COLUMNS: tuple[str, ...] = (
    "chegara k1",
    "chegara lcr",
    "chegara k3",
    "k1 kapital yetarliligi",
    "lcr likvidlik",
    "k3 bir qarzdor",
)

REPORT_SUFFIXES: tuple[str, ...] = (".xlsx", ".xml")
"""Formats the sample only ever uses for aggregate reports."""


class Role(StrEnum):
    """The dataset slot a file fills once ingested."""

    REGISTER = "register"
    NORMATIV = "normativ"
    REPORT = "report"
    UNKNOWN = "unknown"


ROLE_LABELS: dict[Role, str] = {
    Role.REGISTER: "Loan register",
    Role.NORMATIV: "Prudential ratios",
    Role.REPORT: "Aggregate report",
    Role.UNKNOWN: "Unrecognised",
}


def classify_frame(frame: pd.DataFrame) -> Role:
    """Role of an already-parsed CSV, from the marker columns it carries."""
    if resolve_column(frame, NORMATIV_COLUMNS) is not None:
        return Role.NORMATIV
    if resolve_column(frame, INDICATOR_COLUMNS) is not None:
        return Role.REPORT
    if resolve_column(frame, AMOUNT_COLUMNS) is not None and (
        resolve_column(frame, LOAN_ID_COLUMNS) is not None
        or resolve_column(frame, BANK_COLUMNS) is not None
    ):
        return Role.REGISTER
    return Role.UNKNOWN


def classify_file(path: Path) -> Role:
    """Role of a file on disk; `UNKNOWN` for anything unreadable or unrecognised.

    XLSX and XML are aggregate reports by construction -- they have no other use in this
    dataset -- so only CSV needs its columns inspected.
    """
    suffix = path.suffix.lower()
    if suffix in REPORT_SUFFIXES:
        return Role.REPORT
    if suffix != ".csv":
        return Role.UNKNOWN
    try:
        return classify_frame(read_csv_any(path))
    except ValueError:
        return Role.UNKNOWN
