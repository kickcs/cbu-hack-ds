"""Shape of a balance-sheet move: is it broad or concentrated?

One period's per-line changes form a vector. What separates a level shift from window
dressing is that vector's *direction*, not its length: a restatement pushes every line at
once, dressing pushes one or two and leaves the rest alone.

Three independent readings of that direction, deliberately not variations of one idea:

- `breadth`      -- median over max of the changes. Order statistics only: no geometry, no
                    fitted reference, immune to how many lines the report happens to carry.
- `uniformity`   -- cosine between the normalised change vector and the all-ones direction.
                    Pure geometry against a reference fixed a priori, equivalent to a
                    Euclidean distance on the unit sphere: |v̂ − û|² = 2(1 − cos).
- `pc1_alignment`-- projection onto the first principal component of every bank-period in
                    the panel. The reference here is *learned*: instead of assuming that
                    normal co-movement is uniform, it asks the data what normal looks like.

On the sample PC1 explains 72.7 % of the variance and sits at cosine 0.997 to the uniform
direction -- the panel independently confirms the assumption the middle metric makes, which
is why keeping both is worth the few lines.

A move is called concentrated when the majority of the three say so. Any single cut could be
argued with; three readings from different mathematics agreeing is a stronger statement, and
their disagreement is itself worth surfacing to an auditor (`ShapeVerdict.unanimous`).
"""
from __future__ import annotations

from typing import NamedTuple, Sequence

import numpy as np

BREADTH_CUT = 0.20
"""median/max below this reads as concentrated. Sample: 0.064 vs next bank 0.236."""

UNIFORMITY_CUT = 0.65
"""cosine to the uniform direction below this reads as concentrated. Sample: 0.561 vs 0.777."""

PC1_CUT = 0.70
"""projection onto PC1 below this reads as concentrated. Sample: 0.594 vs 0.784."""

_MIN_PANEL_ROWS = 20
"""Below this many bank-periods PC1 is too unstable to be worth consulting."""


class ShapeVerdict(NamedTuple):
    """How broad one period's move was, read three independent ways."""

    breadth: float
    uniformity: float
    pc1_alignment: float | None
    concentrated: bool
    votes: int
    voters: int

    @property
    def unanimous(self) -> bool:
        """Every available metric agreed -- no reason for an auditor to look twice."""
        return self.votes in (0, self.voters)


def breadth(changes: Sequence[float]) -> float:
    """Median change over the largest one: 1.0 when every line moves alike, →0 when one dominates."""
    v = np.abs(np.asarray(changes, dtype=float))
    peak = float(v.max()) if v.size else 0.0
    return float(np.median(v) / peak) if peak else 1.0


def uniformity(changes: Sequence[float]) -> float:
    """Cosine between the change vector and the all-ones direction, in [0, 1]."""
    v = np.abs(np.asarray(changes, dtype=float))
    norm = float(np.linalg.norm(v))
    if not norm or v.size == 0:
        return 1.0
    return float(v @ np.ones(v.size) / (norm * np.sqrt(v.size)))


def fit_pc1(panel: Sequence[Sequence[float]]) -> np.ndarray | None:
    """First principal direction of the panel's change vectors, or None if too few rows.

    Rows are normalised to unit length first: the question is which lines move *together*,
    not how large the move was, and without that a single violent period would define the
    component all by itself.
    """
    matrix = np.abs(np.asarray(panel, dtype=float))
    if matrix.ndim != 2 or matrix.shape[0] < _MIN_PANEL_ROWS:
        return None
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    keep = norms.ravel() > 0
    if keep.sum() < _MIN_PANEL_ROWS:
        return None
    unit = matrix[keep] / norms[keep]
    return np.linalg.svd(unit, full_matrices=False)[2][0]


def pc1_alignment(changes: Sequence[float], pc1: np.ndarray | None) -> float | None:
    """|cosine| between the change vector and the panel's first principal direction."""
    if pc1 is None:
        return None
    v = np.abs(np.asarray(changes, dtype=float))
    norm = float(np.linalg.norm(v))
    if not norm or v.size != pc1.size:
        return None
    return float(abs(v @ pc1) / norm)


def classify(changes: Sequence[float], pc1: np.ndarray | None = None) -> ShapeVerdict:
    """Read the move three ways and let the majority decide whether it is concentrated."""
    b = breadth(changes)
    u = uniformity(changes)
    p = pc1_alignment(changes, pc1)

    ballots = [b < BREADTH_CUT, u < UNIFORMITY_CUT]
    if p is not None:
        ballots.append(p < PC1_CUT)
    votes = sum(ballots)

    return ShapeVerdict(
        breadth=b,
        uniformity=u,
        pc1_alignment=p,
        concentrated=votes * 2 > len(ballots),
        votes=votes,
        voters=len(ballots),
    )
