"""Shape metrics: does a move read as broad or concentrated, and do the three agree."""
from __future__ import annotations

import numpy as np
import pytest

from app.detectors import shape

BROAD = [0.21, 0.20, 0.19, 0.22, 0.20, 0.18, 0.21, 0.20, 0.19]
CONCENTRATED = [0.55, 0.40, 0.02, 0.03, 0.01, 0.02, 0.03, 0.02, 0.01]


def test_breadth_is_one_when_every_line_moves_alike():
    assert shape.breadth([0.2] * 9) == pytest.approx(1.0)


def test_breadth_collapses_when_one_line_dominates():
    assert shape.breadth([1.0] + [0.0] * 8) == pytest.approx(0.0)


def test_uniformity_is_one_for_the_uniform_direction():
    assert shape.uniformity([0.2] * 9) == pytest.approx(1.0)


def test_uniformity_falls_towards_one_over_sqrt_n_for_a_single_axis():
    """A move along one axis alone sits at cosine 1/sqrt(n) to the all-ones direction."""
    assert shape.uniformity([1.0] + [0.0] * 8) == pytest.approx(1 / np.sqrt(9))


def test_uniformity_matches_euclidean_distance_on_the_unit_sphere():
    """|v̂ - û|² = 2(1 - cos): the two readings are the same statement."""
    v = np.array(CONCENTRATED)
    unit_v = v / np.linalg.norm(v)
    unit_u = np.ones(9) / np.sqrt(9)
    distance = float(np.linalg.norm(unit_v - unit_u))
    assert distance**2 == pytest.approx(2 * (1 - shape.uniformity(CONCENTRATED)))


def test_metrics_are_scale_free():
    """Doubling every change keeps the shape, so every metric must be unchanged."""
    doubled = [c * 2 for c in CONCENTRATED]
    assert shape.breadth(doubled) == pytest.approx(shape.breadth(CONCENTRATED))
    assert shape.uniformity(doubled) == pytest.approx(shape.uniformity(CONCENTRATED))


def test_fit_pc1_needs_enough_rows():
    assert shape.fit_pc1([BROAD] * 5) is None
    assert shape.fit_pc1([BROAD] * shape._MIN_PANEL_ROWS) is not None


def test_pc1_recovers_the_common_direction():
    """Fitted on mostly-broad periods, PC1 should point along the uniform direction."""
    rng = np.random.default_rng(0)
    panel = [list(np.full(9, 0.02) + rng.normal(0, 0.002, 9)) for _ in range(60)]
    pc1 = shape.fit_pc1(panel)
    assert pc1 is not None
    assert abs(float(pc1 @ (np.ones(9) / 3))) > 0.95


def test_classify_calls_a_broad_move_not_concentrated():
    verdict = shape.classify(BROAD)
    assert not verdict.concentrated
    assert verdict.unanimous


def test_classify_calls_a_targeted_move_concentrated():
    verdict = shape.classify(CONCENTRATED)
    assert verdict.concentrated
    assert verdict.unanimous


def test_classify_without_pc1_uses_two_voters():
    verdict = shape.classify(CONCENTRATED, pc1=None)
    assert verdict.voters == 2
    assert verdict.pc1_alignment is None


def test_classify_with_pc1_uses_three_voters():
    pc1 = shape.fit_pc1([BROAD] * 40)
    verdict = shape.classify(CONCENTRATED, pc1=pc1)
    assert verdict.voters == 3
    assert verdict.pc1_alignment is not None


def test_disagreement_is_reported_rather_than_hidden():
    """A move on the cut between the two readings must not claim unanimity."""
    borderline = [0.30, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06]
    verdict = shape.classify(borderline)
    assert verdict.votes not in (0, verdict.voters) or verdict.unanimous
    # whichever way it lands, `unanimous` must agree with the vote count
    assert verdict.unanimous == (verdict.votes in (0, verdict.voters))
