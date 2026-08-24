"""Benford's law itself: first-digit extraction, theoretical distribution, MAD and chi-square.

Pure statistics over a sequence of numbers — this module knows nothing about banks,
registers or verdicts. Turning its output into a per-bank result is the job of
`audit/benford_test.py`.

Sources for thresholds:
- Nigrini, M. (2012). "Benford's Law: Applications for Forensic Accounting, Auditing,
  and Fraud Detection". Wiley. MAD decision criteria for first-digit test:
  MAD < 0.006 close conformity, 0.006-0.012 acceptable, 0.012-0.015 marginally
  acceptable, > 0.015 nonconformity.
"""
from __future__ import annotations

import logging
import math
from collections import Counter
from typing import Iterable, Sequence

import numpy as np

log = logging.getLogger(__name__)

FIRST_DIGITS: tuple[int, ...] = tuple(range(1, 10))

# Nigrini (2012) MAD thresholds, first-digit Benford test.
MAD_CLOSE = 0.006
MAD_ACCEPTABLE = 0.012
MAD_MARGINAL = 0.015


def benford_probabilities(digits: Sequence[int] = FIRST_DIGITS) -> dict[int, float]:
    """Theoretical first-digit probabilities P(d) = log10(1 + 1/d)."""
    return {d: math.log10(1.0 + 1.0 / d) for d in digits}


# Same probabilities as an array aligned with FIRST_DIGITS -- the shape every
# numeric routine here actually consumes.
EXPECTED_SHARES: np.ndarray = np.array([benford_probabilities()[d] for d in FIRST_DIGITS])


def first_digit(value: object) -> int | None:
    """First significant digit of a positive finite number; None for invalid input.

    Edge cases handled: non-numeric, NaN/Inf, zero, negative -- all rejected and
    logged, never silently included in the sample.
    """
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        log.warning("Benford: non-numeric value filtered: %r", value)
        return None
    if not math.isfinite(v):
        log.warning("Benford: non-finite value filtered: %r", value)
        return None
    if v <= 0:
        log.warning("Benford: non-positive value filtered: %r", value)
        return None
    return int(v * 10 ** (-math.floor(math.log10(v))))


def extract_first_digits(values: Iterable[object]) -> tuple[np.ndarray, int]:
    """Return (array of first digits 1..9, number of dropped invalid values)."""
    digits: list[int] = []
    dropped = 0
    for v in values:
        d = first_digit(v)
        if d is None:
            dropped += 1
        else:
            digits.append(d)
    return np.asarray(digits, dtype=int), dropped


def empirical_distribution(digits: np.ndarray) -> np.ndarray:
    """Empirical probabilities for digits 1..9 from an array of first digits."""
    if digits.size == 0:
        return np.zeros(len(FIRST_DIGITS))
    counts = Counter(int(d) for d in digits)
    n = len(digits)
    return np.array([counts.get(d, 0) / n for d in FIRST_DIGITS])


def benford_mad(observed: np.ndarray, expected: np.ndarray | None = None) -> float:
    """Mean absolute deviation between empirical and theoretical first-digit shares."""
    if expected is None:
        expected = EXPECTED_SHARES
    return float(np.mean(np.abs(observed - expected)))


def chi_square_test(
    digits: np.ndarray,
    expected: np.ndarray | None = None,
) -> tuple[float, float]:
    """Pearson chi-square goodness-of-fit vs Benford distribution -> (stat, p_value)."""
    if expected is None:
        expected = EXPECTED_SHARES
    if digits.size == 0:
        return float("nan"), 1.0
    observed = np.array([np.sum(digits == d) for d in FIRST_DIGITS], dtype=float)
    expected_counts = expected * digits.size
    return chi_square_from_counts(observed, expected_counts)


def chi_square_from_counts(
    observed: np.ndarray, expected_counts: np.ndarray
) -> tuple[float, float]:
    """chi-square statistic and p-value from observed/expected counts."""
    from scipy.stats import chisquare

    mask = expected_counts > 0
    stat, p = chisquare(observed[mask], expected_counts[mask], ddof=0)
    return float(stat), float(p)


def mad_label(mad: float) -> str:
    """Nigrini (2012) verbal interpretation of the MAD value."""
    if mad < MAD_CLOSE:
        return "close"
    if mad < MAD_ACCEPTABLE:
        return "acceptable"
    if mad < MAD_MARGINAL:
        return "marginally_acceptable"
    return "nonconformity"
