"""Tests for the Benford engine and the small-sample guard (TZ §11)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from app import audit, benford

# Synthetic numbers whose first digits follow Benford's law exactly in expectation.
BENFORD_DIGITS = np.random.default_rng(7).choice(
    range(1, 10), size=50_000, p=[benford.benford_probabilities()[d] for d in range(1, 10)]
)


def _amount_for_digit(d: int, rng: np.random.Generator) -> float:
    """A random positive amount whose first digit is exactly d."""
    k = int(rng.uniform(0, 3))
    return d * 10.0 ** k * rng.uniform(1.0, 1.0 + 1.0 / d)


def test_benford_following_data_mad_close_to_zero():
    """A large sample honestly following Benford's law yields MAD near zero."""
    rng = np.random.default_rng(1)
    amounts = [_amount_for_digit(int(d), rng) for d in BENFORD_DIGITS[:20_000]]
    res = audit.run_benford(amounts)
    assert res.n == 20_000
    assert res.mad is not None and res.mad < 0.01
    assert res.mad_label in ("close", "acceptable")


def test_benford_following_data_not_flagged():
    amounts = [_amount_for_digit(int(d), np.random.default_rng(2)) for d in BENFORD_DIGITS[:5_000]]
    res = audit.run_benford(amounts)
    assert res.sufficient
    assert not res.flagged


def test_benford_manipulated_data_flagged():
    """First digits all equal to 1 deviate strongly from Benford -> flagged."""
    rng = np.random.default_rng(5)
    amounts = [10.0 ** (i % 9 + 1) * rng.uniform(1.0, 2.0) for i in range(400)]
    res = audit.run_benford(amounts)
    assert res.n >= audit.MIN_SAMPLE
    assert res.flagged
    assert res.mad > 0.1


def test_small_sample_returns_insufficient_flag():
    """n < 300 -> explicit insufficient-sample flag, no numeric MAD decision."""
    rng = np.random.default_rng(3)
    amounts = [_amount_for_digit(int(d), rng) for d in BENFORD_DIGITS[:50]]
    res = audit.run_benford(amounts)
    assert res.n == 50
    assert not res.sufficient
    assert not res.flagged  # never mark a bank suspicious on an undersized sample


def test_is_sample_sufficient_boundary():
    assert not audit.is_sample_sufficient(299)
    assert audit.is_sample_sufficient(300)
    assert audit.is_sample_sufficient(2600)


def test_first_digit_edges():
    assert benford.first_digit(0) is None
    assert benford.first_digit(-123) is None
    assert benford.first_digit("abc") is None
    assert benford.first_digit(float("nan")) is None
    assert benford.first_digit(150075575) == 1
    assert benford.first_digit(9_999_999) == 9
    assert benford.first_digit(1.0) == 1


def test_benford_distribution_sums_to_one():
    probs = benford.benford_probabilities()
    assert math.isclose(sum(probs.values()), 1.0, rel_tol=1e-9)
    assert list(probs) == list(range(1, 10))


def test_theoretical_leading_digit_monotonic():
    probs = benford.benford_probabilities()
    vals = [probs[d] for d in range(1, 10)]
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))


def test_chi_square_on_honest_data():
    amounts = [_amount_for_digit(int(d), np.random.default_rng(4)) for d in BENFORD_DIGITS[:5_000]]
    res = audit.run_benford(amounts)
    assert res.chi2 is not None
    assert res.chi2_p > 0.01


def test_bootstrap_threshold_reasonable():
    t = benford.bootstrap_mad_threshold(2000, n_boot=300)
    assert 0.003 < t < 0.015
