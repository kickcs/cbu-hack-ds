"""Benford's law: the statistical engine and its bootstrap calibration.

- `law.py`         -- first digits, theoretical shares, MAD, chi-square, Nigrini labels;
- `calibration.py` -- empirical threshold for a given sample size (bonus).

Both are re-exported here, so callers import one name: `from app import benford`.
"""
from __future__ import annotations

from .calibration import bootstrap_chi2_threshold, bootstrap_mad_threshold
from .law import (
    EXPECTED_SHARES,
    FIRST_DIGITS,
    MAD_ACCEPTABLE,
    MAD_CLOSE,
    MAD_MARGINAL,
    benford_mad,
    benford_probabilities,
    chi_square_from_counts,
    chi_square_test,
    empirical_distribution,
    extract_first_digits,
    first_digit,
    mad_label,
)

__all__ = [
    "EXPECTED_SHARES",
    "FIRST_DIGITS",
    "MAD_ACCEPTABLE",
    "MAD_CLOSE",
    "MAD_MARGINAL",
    "benford_mad",
    "benford_probabilities",
    "bootstrap_chi2_threshold",
    "bootstrap_mad_threshold",
    "chi_square_from_counts",
    "chi_square_test",
    "empirical_distribution",
    "extract_first_digits",
    "first_digit",
    "mad_label",
]
