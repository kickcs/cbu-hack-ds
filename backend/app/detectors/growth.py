"""Growth-jump detectors over the total-assets series.

Both share the same month-over-month growth computation and differ only in which
jump they look at: discontinuity inspects transitions between non-final periods,
window dressing inspects the transition into the final reporting period.
Thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

from abc import abstractmethod

import numpy as np
import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, bank_report, empty_evidence

GROWTH_JUMP = 0.15  # relative month-over-month jump to fire
_MIN_PERIODS = 4  # too few periods -> the series can't show a meaningful jump


def total_assets_series(report: pd.DataFrame, bank: str) -> list[float]:
    g = report[(report["bank"] == bank) & (report["indicator"] == "jami_aktivlar")]
    return [float(v) for v in g.sort_values("period")["summa"]]


def growth_rates(series: list[float]) -> list[float]:
    return [
        abs(series[i] - series[i - 1]) / abs(series[i - 1])
        for i in range(1, len(series))
        if series[i - 1]
    ]


class GrowthJumpDetector(Detector):
    """Common scoring: pick one jump from the growth series, flag if it is large."""

    title: str
    summary: str

    @abstractmethod
    def _jump_index(self, growth: list[float]) -> int | None:
        """Index (into `growth`) of the transition this detector inspects."""

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        for bank in sorted(ctx.report["bank"].unique()):
            score, flagged = 0.0, False
            series = total_assets_series(ctx.report, bank)
            if len(series) >= _MIN_PERIODS:
                growth = growth_rates(series)
                idx = self._jump_index(growth)
                if idx is not None:
                    score = float(growth[idx])
                    flagged = bool(score > GROWTH_JUMP)
            rows.append({"bank": bank, "score": score, "flagged": flagged})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        series = total_assets_series(ctx.report, bank)
        if len(series) < _MIN_PERIODS:
            return empty_evidence()
        growth = growth_rates(series)
        idx = self._jump_index(growth)
        if idx is None:
            return empty_evidence()
        periods = sorted(bank_report(ctx.report, bank)["period"].unique())
        rows = [
            {
                "transition": f"{periods[idx]} → {periods[idx + 1]}",
                "before": round(series[idx], 2),
                "after": round(series[idx + 1], 2),
                "growth": round(growth[idx], 4),
                "suspect": True,
            }
        ]
        return {"test": self.name, "title": self.title, "summary": self.summary, "rows": rows}


class DiscontinuityDetector(GrowthJumpDetector):
    """A large jump in total assets between two non-final periods."""

    name = "discontinuity"
    title = "Break in the reported series"
    summary = "Total assets jump between consecutive months."

    def _jump_index(self, growth: list[float]) -> int | None:
        mid = growth[:-1]
        return int(np.argmax(mid)) if mid else None


class WindowDressingDetector(GrowthJumpDetector):
    """A large jump in total assets into the final reporting period."""

    name = "window_dressing"
    title = "Spike in the closing period"
    summary = "Total assets grow abnormally into the year end."

    def _jump_index(self, growth: list[float]) -> int | None:
        return len(growth) - 1 if growth else None
