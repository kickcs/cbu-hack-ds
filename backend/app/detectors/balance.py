"""Balance-identity check (TZ §4 bonus): total assets must equal total
liabilities + capital in every period -- an accounting identity, not a hypothesis.

Tolerance is an engineering 0.01% for float aggregation noise; a real breach is
orders of magnitude above it. Advisory -- documented in DECISIONS.md §4.
"""
from __future__ import annotations

from typing import Iterator, NamedTuple

import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, bank_report

BALANCE_TOLERANCE = 0.0001  # |aktiv - passiv| / |aktiv|

_AKTIV_TOTAL = "jami_aktivlar"
_PASSIV_TOTAL = "jami_passivlar"


class BalanceMismatch(NamedTuple):
    period: object
    aktiv: float
    passiv: float
    ratio: float


def _mismatches(bank_rows: pd.DataFrame) -> Iterator[BalanceMismatch]:
    """Per-period comparison of the two balance totals."""
    for period, pg in bank_rows.groupby("period"):
        aktiv = pg[pg["indicator"] == _AKTIV_TOTAL]["summa"]
        passiv = pg[pg["indicator"] == _PASSIV_TOTAL]["summa"]
        if aktiv.empty or passiv.empty:
            continue
        a = float(aktiv.iloc[0])
        if a == 0:
            continue
        p = float(passiv.iloc[0])
        yield BalanceMismatch(period, a, p, abs(a - p) / abs(a))


class BalanceIdentityDetector(Detector):
    name = "balance"
    advisory = True

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        for bank, g in ctx.report.groupby("bank"):
            worst = max((m.ratio for m in _mismatches(g)), default=0.0)
            rows.append({"bank": str(bank), "score": worst, "flagged": bool(worst > BALANCE_TOLERANCE)})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        rows = []
        for m in _mismatches(bank_report(ctx.report, bank)):
            if m.ratio > BALANCE_TOLERANCE:
                rows.append(
                    {
                        "period": str(m.period),
                        "total_assets": round(m.aktiv, 2),
                        "total_liabilities": round(m.passiv, 2),
                        "gap": round(m.aktiv - m.passiv, 2),
                        "gap_share": round(m.ratio, 6),
                        "suspect": True,
                    }
                )
        rows.sort(key=lambda r: r["period"])
        return {
            "test": self.name,
            "title": "Assets do not equal liabilities",
            "title_key": "evidence.blocks.balance.title",
            "summary": "Reported assets differ from reported liabilities, breaking the accounting identity.",
            "summary_key": "evidence.blocks.balance.summary",
            "summary_args": {},
            "rows": rows,
        }
