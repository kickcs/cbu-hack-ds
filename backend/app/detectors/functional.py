"""Functional façade over the detector classes: one `detect_*` call per violation type.

The audit pipeline drives detectors through the registry, but the tests want to score a
single DataFrame without assembling an `AuditContext` first. These wrappers are that
shortcut -- they add no logic of their own.
"""
from __future__ import annotations

import pandas as pd

from .arithmetic import ArithmeticDetector
from .balance import BalanceIdentityDetector
from .base import AuditContext
from .growth import DiscontinuityDetector, WindowDressingDetector
from .last_digit import LastDigitUniformityDetector
from .rounding import RoundingDetector
from .threshold import ThresholdClusteringDetector


def detect_threshold(normativ: pd.DataFrame) -> pd.DataFrame:
    """K1 readings clustering just above the regulatory limit."""
    return ThresholdClusteringDetector().run(AuditContext(normativ=normativ))


def detect_rounding(report: pd.DataFrame) -> pd.DataFrame:
    """Reported figures ending in an implausibly long run of zeros."""
    return RoundingDetector().run(AuditContext(report=report))


def detect_arithmetic(report: pd.DataFrame) -> pd.DataFrame:
    """Total assets that do not match the sum of their components."""
    return ArithmeticDetector().run(AuditContext(report=report))


def detect_discontinuity(report: pd.DataFrame) -> pd.DataFrame:
    """A break in the total-assets series between two ordinary months."""
    return DiscontinuityDetector().run(AuditContext(report=report))


def detect_window_dressing(report: pd.DataFrame) -> pd.DataFrame:
    """A spike in total assets into the closing period."""
    return WindowDressingDetector().run(AuditContext(report=report))


def detect_last_digit(register: pd.DataFrame) -> pd.DataFrame:
    """Last digit of loan amounts departing from the uniform expectation."""
    return LastDigitUniformityDetector().run(AuditContext(register=register))


def detect_balance(report: pd.DataFrame) -> pd.DataFrame:
    """Assets not equal to liabilities plus capital."""
    return BalanceIdentityDetector().run(AuditContext(report=report))
