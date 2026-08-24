"""Shape of the result file: which banks it lists and under which column names.

The spec exists in two language variants demanding different headers for the same table, and
which one the day-2 autocheck reads is unknown, so every run writes both (see `config.py`).
Only the column names differ -- the rows are identical.

Column names and row format are checked by the autocheck: do not change them.
"""
from __future__ import annotations

import pandas as pd

from ..domain import BankAudit

RESULT_COLUMNS = ("банк", "значение_mad", "причина")
"""Russian spec §8."""

NATIJA_COLUMNS = ("bank", "mad_qiymati", "sabab")
"""Official uzbek spec §5."""

REASON_SEPARATOR = "|"


def to_suspicious_frame(audits: list[BankAudit], columns=RESULT_COLUMNS) -> pd.DataFrame:
    """Suspicious banks only, one row each: name, headline metric, reasons."""
    rows = [
        (a.bank, round(a.primary_metric(), 6), REASON_SEPARATOR.join(a.reason))
        for a in audits
        if a.suspicious
    ]
    return pd.DataFrame(rows, columns=list(columns))
