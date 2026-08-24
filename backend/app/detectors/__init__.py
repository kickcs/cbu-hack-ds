"""Aggregate-report detectors: one module per violation type, one shared contract.

Each detector owns both sides of its violation -- the scoring (`run`) and the evidence an
auditor would eyeball (`evidence`) -- so the trigger logic exists in exactly one place; see
`base.py`. `registry.py` fixes the set and the order in which they run; adding a test means
adding one module and one line there, leaving the audit core untouched.

  base.py        Detector contract, AuditContext, evidence block shape
  registry.py    the ordered set of detectors (order = order of reasons in the result CSV)
  functional.py  detect_* shortcuts for the tests and the notebook

  threshold.py   K1 clustering just above the regulatory limit
  rounding.py    implausibly round reported figures
  arithmetic.py  total assets that do not foot
  growth.py      discontinuity and window dressing (one growth-jump base class)
  last_digit.py  non-uniform last digit of loan amounts       (advisory)
  balance.py     assets != liabilities + capital              (advisory)

All thresholds are grounded in the sample data (see DECISIONS.md §4) and chosen to separate
the six corrupted banks from clean ones with a wide margin; they also hold for the closed
day-2 dataset, which follows the same generation rules.
"""
from __future__ import annotations

from .arithmetic import ARITHMETIC_RATIO, ArithmeticDetector
from .balance import BALANCE_TOLERANCE, BalanceIdentityDetector
from .base import AuditContext, Detector, EvidenceBlock
from .functional import (
    detect_arithmetic,
    detect_balance,
    detect_discontinuity,
    detect_last_digit,
    detect_rounding,
    detect_threshold,
    detect_window_dressing,
)
from .growth import (
    GROWTH_JUMP,
    DiscontinuityDetector,
    WindowDressingDetector,
    total_assets_series,
)
from .last_digit import LAST_DIGIT_ALPHA, LastDigitUniformityDetector, last_digits
from .registry import ADVISORY, BY_NAME, DETECTORS
from .rounding import ROUNDING_FRACTION, ROUNDING_TRAILING_ZEROS, RoundingDetector, trailing_zeros
from .threshold import THRESHOLD_BAND, THRESHOLD_FRACTION, ThresholdClusteringDetector

__all__ = [
    "ADVISORY",
    "ARITHMETIC_RATIO",
    "BALANCE_TOLERANCE",
    "BY_NAME",
    "DETECTORS",
    "GROWTH_JUMP",
    "LAST_DIGIT_ALPHA",
    "ROUNDING_FRACTION",
    "ROUNDING_TRAILING_ZEROS",
    "THRESHOLD_BAND",
    "THRESHOLD_FRACTION",
    "ArithmeticDetector",
    "AuditContext",
    "BalanceIdentityDetector",
    "Detector",
    "DiscontinuityDetector",
    "EvidenceBlock",
    "LastDigitUniformityDetector",
    "RoundingDetector",
    "ThresholdClusteringDetector",
    "WindowDressingDetector",
    "detect_arithmetic",
    "detect_balance",
    "detect_discontinuity",
    "detect_last_digit",
    "detect_rounding",
    "detect_threshold",
    "detect_window_dressing",
    "last_digits",
    "total_assets_series",
    "trailing_zeros",
]
