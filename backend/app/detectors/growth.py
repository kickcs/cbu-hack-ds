"""Growth-jump detectors over the aggregate report.

Both detectors look at the same event -- the period in which some balance line moves most
sharply -- and split on the *shape* of that move rather than on where it sits in the file:

- a **level shift** moves every line at once (a restatement, a merger, a scaling error), so
  the median line moves about as much as the largest one -> `discontinuity`;
- **window dressing** inflates only the handful of lines a regulator reads for liquidity
  (cash, retail deposits) and leaves the rest flat, so the median line barely moves while
  one or two spike -> `window_dressing`.

The direction of that change vector is read three independent ways in `shape.py` --
an order statistic (`breadth`), a fixed geometric reference (`uniformity`) and one learned
from the panel by PCA (`pc1_alignment`) -- and the majority decides. All three are scale-free,
computed inside a single bank-period, and independent of which period the jump lands in.

The detection signal is the largest *per-line* change, not the change in total assets.
Dressing a small line barely moves the total: on the sample the flagged banks reach 0.29 and
0.55 by line against 0.21 and 0.16 by total, while clean banks stay at 0.060 by line -- so
the line signal both separates further (4.9x vs 3.1x) and catches dressing the total hides.

Thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

from abc import abstractmethod
from typing import NamedTuple

import pandas as pd

from .base import AuditContext, Detector, EvidenceBlock, empty_evidence
from .shape import ShapeVerdict, classify, fit_pc1

LINE_JUMP = 0.15
"""Largest relative MoM move of any single balance line that counts as an event.

Sample separation: clean banks peak at 0.060, flagged banks at 0.294 and 0.553.
"""

GROWTH_JUMP = LINE_JUMP  # backwards-compatible alias for the public package export

_MIN_PERIODS = 4  # too few periods -> the series can't show a meaningful jump

_TOTAL_INDICATOR = "jami_aktivlar"

BREADTH_ITEMS: tuple[str, ...] = (
    "naqd_pullar",
    "banklararo_joylashtirishlar",
    "kredit_portfeli",
    "qimmatli_qogozlar",
    "asosiy_vositalar",
    "depozitlar_aholi",
    "depozitlar_yuridik",
    "banklararo_qarzlar",
    "chiqarilgan_qimmatli_qogozlar",
)
"""Lines whose co-movement defines breadth.

The two totals are excluded because they are sums of the rest; `kredit_zaxirasi` and
`kapital` because both swing by tens of percent on their own -- the reserve is small and
lumpy, the capital line absorbs whatever the other passives leave over -- and either would
dominate the maximum without saying anything about how broad the move was.
"""


class Jump(NamedTuple):
    """The sharpest per-line move in a bank's report, and how broad that period was."""

    period: object
    previous_period: object
    line: str
    line_change: float
    total_change: float
    shape: ShapeVerdict
    changes: dict[str, float]


def change_panel(report: pd.DataFrame, items: list[str]) -> list[list[float]]:
    """Per-line relative changes for every bank-period -- the sample PC1 is fitted on."""
    rows: list[list[float]] = []
    for _, g in report.groupby("bank"):
        wide = g.pivot_table(index="period", columns="indicator", values="summa", aggfunc="first")
        present = [c for c in items if c in wide.columns]
        if len(present) != len(items):
            continue
        changes = wide.sort_index()[items].pct_change().abs().dropna()
        rows.extend(changes.to_numpy(dtype=float).tolist())
    return rows


def _pivot(report: pd.DataFrame, bank: str) -> pd.DataFrame:
    g = report[report["bank"] == bank]
    return g.pivot_table(
        index="period", columns="indicator", values="summa", aggfunc="first"
    ).sort_index()


def largest_jump(report: pd.DataFrame, bank: str, pc1=None) -> Jump | None:
    """Period whose sharpest balance-line move is the largest, with that period's breadth."""
    wide = _pivot(report, bank)
    items = [c for c in BREADTH_ITEMS if c in wide.columns]
    if len(wide) < _MIN_PERIODS or not items:
        return None

    changes = wide.pct_change().abs()
    per_period = changes[items].dropna(how="all")
    if per_period.empty:
        return None

    period = per_period.max(axis=1).idxmax()
    row = per_period.loc[period].dropna()
    if row.empty:
        return None

    peak = float(row.max())
    idx = list(wide.index).index(period)
    total_change = (
        float(changes.loc[period, _TOTAL_INDICATOR])
        if _TOTAL_INDICATOR in changes.columns and pd.notna(changes.loc[period, _TOTAL_INDICATOR])
        else 0.0
    )

    return Jump(
        period=period,
        previous_period=wide.index[idx - 1],
        line=str(row.idxmax()),
        line_change=peak,
        total_change=total_change,
        shape=classify(row.to_numpy(dtype=float), pc1),
        changes={k: float(v) for k, v in row.items()},
    )


def shape_note(shape: ShapeVerdict) -> str:
    """One sentence on how the three shape metrics voted, for the evidence summary."""
    parts = [f"breadth {shape.breadth:.2f}", f"uniformity {shape.uniformity:.2f}"]
    if shape.pc1_alignment is not None:
        parts.append(f"PC1 alignment {shape.pc1_alignment:.2f}")
    agreement = "all agree" if shape.unanimous else f"{shape.votes} of {shape.voters} agree"
    return f" Shape metrics: {', '.join(parts)} ({agreement})."


class GrowthJumpDetector(Detector):
    """Common scoring: find the sharpest move, fire when its shape matches this detector."""

    title: str
    summary: str

    @abstractmethod
    def _shape_matches(self, shape: ShapeVerdict) -> bool:
        """Whether a move of this shape is the kind this detector reports."""

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        items = [c for c in BREADTH_ITEMS if c in set(ctx.report["indicator"])]
        pc1 = fit_pc1(change_panel(ctx.report, items)) if items else None
        rows = []
        for bank in sorted(ctx.report["bank"].unique()):
            score, flagged = 0.0, False
            jump = largest_jump(ctx.report, bank, pc1)
            if jump is not None and jump.line_change > LINE_JUMP and self._shape_matches(jump.shape):
                score, flagged = jump.line_change, True
            rows.append({"bank": bank, "score": score, "flagged": flagged})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        items = [c for c in BREADTH_ITEMS if c in set(ctx.report["indicator"])]
        pc1 = fit_pc1(change_panel(ctx.report, items)) if items else None
        jump = largest_jump(ctx.report, bank, pc1)
        if jump is None:
            return empty_evidence()
        transition = f"{jump.previous_period} → {jump.period}"
        # Key stays `growth`: the dashboard formats that field as a percentage
        # (frontend/src/entities/bank/lib/format-evidence.ts), and renaming it would
        # silently drop the evidence table back to raw decimals.
        rows = [
            {
                "transition": transition,
                "indicator": _TOTAL_INDICATOR,
                "growth": round(jump.total_change, 4),
                "suspect": False,
            }
        ] + [
            {
                "transition": transition,
                "indicator": name,
                "growth": round(value, 4),
                "suspect": value > LINE_JUMP,
            }
            for name, value in sorted(jump.changes.items(), key=lambda kv: -kv[1])
        ]
        return {
            "test": self.name,
            "title": self.title,
            "summary": self.summary.format(
                line=jump.line,
                change=f"{jump.line_change:.1%}",
                breadth=f"{jump.shape.breadth:.2f}",
                period=jump.period,
            )
            + shape_note(jump.shape),
            "rows": rows,
        }


class DiscontinuityDetector(GrowthJumpDetector):
    """A large move that carries the whole balance sheet at once -- a level shift."""

    name = "discontinuity"
    title = "Break in the reported series"
    summary = (
        "In {period} the sharpest line ({line}) moves {change} and every other line moves "
        "with it (breadth {breadth}) -- a level shift rather than a single mis-stated figure."
    )

    def _shape_matches(self, shape: ShapeVerdict) -> bool:
        return not shape.concentrated


class WindowDressingDetector(GrowthJumpDetector):
    """A large move carried by a couple of lines while the rest stay flat."""

    name = "window_dressing"
    title = "Targeted spike in reported figures"
    summary = (
        "In {period} {line} jumps {change} while the rest of the balance sheet stays flat "
        "(breadth {breadth}) -- the signature of inflating the figures a regulator reads."
    )

    def _shape_matches(self, shape: ShapeVerdict) -> bool:
        return shape.concentrated
