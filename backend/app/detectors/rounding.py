"""Rounding detector: too many reported values ending in a long run of zeros.

Thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, bank_report

ROUNDING_TRAILING_ZEROS = 6  # value considered "rounded" if it ends with 6+ zeros
ROUNDING_FRACTION = 0.3  # min share of rounded values to fire


def trailing_zeros(value: float) -> int:
    s = str(abs(int(value)))
    return len(s) - len(s.rstrip("0"))


def is_rounded(value: float) -> bool:
    return trailing_zeros(value) >= ROUNDING_TRAILING_ZEROS


class RoundingDetector(Detector):
    name = "rounding"

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        for bank, g in ctx.report.groupby("bank"):
            vals = pd.to_numeric(g["summa"], errors="coerce").dropna()
            if vals.empty:
                rows.append({"bank": bank, "score": 0.0, "flagged": False})
                continue
            frac = sum(1 for v in vals if is_rounded(v)) / len(vals)
            rows.append({"bank": bank, "score": float(frac), "flagged": bool(frac >= ROUNDING_FRACTION)})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        rows = []
        for _, r in bank_report(ctx.report, bank).iterrows():
            v = float(r["summa"])
            if is_rounded(v):
                rows.append(
                    {
                        "period": str(r["period"]),
                        "indicator": r["indicator"],
                        "value": int(v),
                        "trailing_zeros": int(trailing_zeros(v)),
                        "suspect": True,
                    }
                )
        rows.sort(key=lambda r: (r["period"], -r["trailing_zeros"]))
        return {
            "test": self.name,
            "title": "Implausibly round figures",
            "summary": f"{len(rows)} reported figures end in {ROUNDING_TRAILING_ZEROS} or more zeros.",
            "rows": rows,
        }
