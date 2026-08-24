"""Bootstrap calibration of the Benford threshold (bonus).

Instead of relying only on the fixed Nigrini thresholds in `law.py`, generate N synthetic
samples of the same size n that honestly follow Benford's law, compute the MAD (or
chi-square) statistic on each, and take the 95th percentile as an empirical decision
threshold. This makes the threshold adaptive to the sample size -- larger samples give a
tighter threshold, and it gives a defensible argument in DECISIONS.md.

The calibrated value is reported next to the verdict in the dashboard as a confirmation;
the verdict itself is still decided by the Nigrini threshold.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .law import EXPECTED_SHARES, FIRST_DIGITS, benford_mad

_CACHE: dict[tuple, float] = {}


def _bootstrap_percentile(
    sample_size: int,
    statistic: Callable[[np.ndarray], float],
    n_boot: int,
    percentile: float,
    seed: int,
) -> float:
    """Percentile of `statistic` over honest Benford samples of a given size.

    `statistic` receives raw per-digit counts (aligned with FIRST_DIGITS).
    """
    if sample_size < 1:
        return float("nan")
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        sample = rng.choice(FIRST_DIGITS, size=sample_size, p=EXPECTED_SHARES)
        counts = np.bincount(sample, minlength=10)[1:10].astype(float)
        stats.append(statistic(counts))
    return float(np.percentile(stats, percentile))


def bootstrap_mad_threshold(
    sample_size: int,
    n_boot: int = 1000,
    percentile: float = 95.0,
    seed: int = 42,
) -> float:
    """Empirical 95th-percentile MAD for honest Benford data of given sample size."""
    key = ("mad", sample_size, n_boot, percentile, seed)
    if key not in _CACHE:
        _CACHE[key] = _bootstrap_percentile(
            sample_size,
            lambda counts: benford_mad(counts / sample_size, EXPECTED_SHARES),
            n_boot, percentile, seed,
        )
    return _CACHE[key]


def bootstrap_chi2_threshold(
    sample_size: int,
    n_boot: int = 1000,
    percentile: float = 95.0,
    seed: int = 42,
) -> float:
    """Empirical 95th-percentile chi-square statistic for honest Benford data."""
    from scipy.stats import chisquare

    expected = EXPECTED_SHARES * sample_size

    def stat(counts: np.ndarray) -> float:
        chi2, _ = chisquare(counts, expected)
        return float(chi2)

    return _bootstrap_percentile(sample_size, stat, n_boot, percentile, seed)
