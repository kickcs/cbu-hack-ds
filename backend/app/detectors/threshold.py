"""Threshold clustering: K1 values sitting in a narrow band just above their limit.

A bank whose K1 readings keep landing inside (chegara, chegara + BAND] instead of
varying freely is suspect. Thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock

THRESHOLD_BAND = 0.005  # band above the K1 limit: (chegara, chegara + 0.005]
THRESHOLD_FRACTION = 0.6  # min share of readings inside the band to fire
_MIN_READINGS = 4


def _k1_limit(g: pd.DataFrame) -> float:
    return pd.to_numeric(g["chegara_k1"], errors="coerce").max()


def _in_band(k1: float, limit: float) -> bool:
    return bool(np.isfinite(limit) and limit < k1 <= limit + THRESHOLD_BAND)


class ThresholdClusteringDetector(Detector):
    name = "threshold"
    requires = ("normativ",)

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        for bank, g in ctx.normativ.groupby("bank"):
            limit = _k1_limit(g)
            k1 = pd.to_numeric(g["k1_kapital_yetarliligi"], errors="coerce").dropna()
            if len(k1) == 0 or not np.isfinite(limit):
                rows.append({"bank": bank, "score": 0.0, "flagged": False})
                continue
            in_band = ((k1 > limit) & (k1 <= limit + THRESHOLD_BAND)).mean()
            flagged = bool(in_band >= THRESHOLD_FRACTION and len(k1) >= _MIN_READINGS)
            rows.append({"bank": bank, "score": float(in_band), "flagged": flagged})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        g = ctx.normativ[ctx.normativ["bank"] == bank]
        limit = _k1_limit(g)
        rows = []
        for _, r in g.iterrows():
            k1 = float(r["k1_kapital_yetarliligi"])
            rows.append(
                {
                    "period": str(r["oy"]),
                    "K1": round(k1, 4),
                    "limit": round(float(limit), 4),
                    "margin": round(k1 - float(limit), 4),
                    "suspect": _in_band(k1, limit),
                }
            )
        rows.sort(key=lambda r: r["period"])
        return {
            "test": self.name,
            "title": "Clustering just above the K1 limit",
            "summary": f"{sum(1 for r in rows if r['suspect'])} of {len(rows)} K1 readings sit in a narrow band "
            f"just above the regulatory limit (limit, limit+{THRESHOLD_BAND}].",
            "rows": rows,
        }
