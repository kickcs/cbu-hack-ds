"""Small-sample guard shared by every register-based statistical test (TZ §5).

Both the Benford test (`audit/benford_test.py`) and the last-digit test
(`detectors/last_digit.py`) run on the loan register and must refuse to draw a
verdict when a bank contributes too few rows: below `MIN_SAMPLE` the sampling noise
of the first-digit distribution is wider than the deviation the test looks for, so
a small clean bank would be indistinguishable from a corrupted one.

Lives at the top level (rather than inside `audit/` or `detectors/`) because both
packages need it and either home would make their imports circular.
"""
from __future__ import annotations

MIN_SAMPLE = 300


def is_sample_sufficient(n: int) -> bool:
    """True when `n` observations are enough for a register-based test to decide."""
    return n >= MIN_SAMPLE
