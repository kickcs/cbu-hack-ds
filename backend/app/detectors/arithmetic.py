"""Arithmetic detector: jami_aktivlar does not reconcile with its components.

Thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

from typing import Iterator, NamedTuple

import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, bank_report

ARITHMETIC_RATIO = 0.001  # |jami - sum(components)| / |jami| threshold

_TOTAL_INDICATOR = "jami_aktivlar"


class Reconciliation(NamedTuple):
    period: object
    total: float
    components: float
    ratio: float


def _reconciliations(bank_rows: pd.DataFrame) -> Iterator[Reconciliation]:
    """Per-period comparison of the assets total line against its components."""
    for period, pg in bank_rows.groupby("period"):
        aktiv = pg[pg["tip"].astype(str).str.lower().str.contains("aktiv")]
        jami = aktiv[aktiv["indicator"] == _TOTAL_INDICATOR]["summa"]
        comp = aktiv[aktiv["indicator"] != _TOTAL_INDICATOR]["summa"]
        if len(jami) == 0 or comp.empty:
            continue
        j, c = float(jami.iloc[0]), float(comp.sum())
        if j == 0:
            continue
        yield Reconciliation(period, j, c, abs(j - c) / abs(j))


class ArithmeticDetector(Detector):
    name = "arithmetic"

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        for bank, g in ctx.report.groupby("bank"):
            worst = max((r.ratio for r in _reconciliations(g)), default=0.0)
            rows.append({"bank": bank, "score": worst, "flagged": bool(worst > ARITHMETIC_RATIO)})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        rows = []
        for r in _reconciliations(bank_report(ctx.report, bank)):
            if r.ratio > ARITHMETIC_RATIO:
                rows.append(
                    {
                        "period": str(r.period),
                        "total_assets": round(r.total, 2),
                        "sum_of_parts": round(r.components, 2),
                        "gap": round(r.total - r.components, 2),
                        "suspect": True,
                    }
                )
        rows.sort(key=lambda r: r["period"])
        return {
            "test": self.name,
            "title": "Total assets do not foot",
            "title_key": "evidence.blocks.arithmetic.title",
            "summary": "The reported assets total does not match the sum of its components.",
            "summary_key": "evidence.blocks.arithmetic.summary",
            "summary_args": {},
            "rows": rows,
        }
