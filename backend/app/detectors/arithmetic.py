"""Arithmetic detector: jami_aktivlar does not reconcile with its components.

Thresholds are documented in DECISIONS.md §4.

A period is only judged when every expected asset component is present. An indicator that
ingestion failed to map is dropped upstream (`ingest/readers.py`), and a missing component
would shrink the component sum by its full value -- indistinguishable from a fabricated
total. Refusing to judge such a period is the difference between "no verdict" and a false
accusation, which the scoring penalises.
"""
from __future__ import annotations

import logging
from typing import Iterator, NamedTuple

import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, bank_report

log = logging.getLogger(__name__)

ARITHMETIC_RATIO = 0.001  # |jami - sum(components)| / |jami| threshold

_TOTAL_INDICATOR = "jami_aktivlar"

EXPECTED_ASSET_COMPONENTS: frozenset[str] = frozenset(
    {
        "naqd_pullar",
        "banklararo_joylashtirishlar",
        "kredit_portfeli",
        "kredit_zaxirasi",
        "qimmatli_qogozlar",
        "asosiy_vositalar",
    }
)
"""Asset lines that must all be present before the total can be checked against them."""


class Reconciliation(NamedTuple):
    period: object
    total: float
    components: float
    ratio: float


def missing_components(indicators: set[str]) -> set[str]:
    """Expected asset components absent from one period's report lines."""
    return set(EXPECTED_ASSET_COMPONENTS) - indicators


def _reconciliations(bank_rows: pd.DataFrame) -> Iterator[Reconciliation]:
    """Per-period comparison of the assets total line against its components.

    Periods with an incomplete component set are skipped with a warning rather than scored.
    """
    for period, pg in bank_rows.groupby("period"):
        aktiv = pg[pg["tip"].astype(str).str.lower().str.contains("aktiv")]
        jami = aktiv[aktiv["indicator"] == _TOTAL_INDICATOR]["summa"]
        comp = aktiv[aktiv["indicator"] != _TOTAL_INDICATOR]
        if len(jami) == 0 or comp.empty:
            continue
        absent = missing_components(set(comp["indicator"]))
        if absent:
            log.warning(
                "arithmetic: period %s skipped, unmapped asset components: %s",
                period,
                sorted(absent),
            )
            continue
        j, c = float(jami.iloc[0]), float(comp["summa"].sum())
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
            "summary": "The reported assets total does not match the sum of its components.",
            "rows": rows,
        }
