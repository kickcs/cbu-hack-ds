"""Ordered detector registry.

The order is load-bearing: it defines the order of `reason` entries in audit
results and therefore in the result CSV ("причина" column). Advisory detectors
come last; they never enter `reason` (see base.Detector.advisory).
"""
from __future__ import annotations

from .arithmetic import ArithmeticDetector
from .balance import BalanceIdentityDetector
from .base import Detector
from .growth import DiscontinuityDetector, WindowDressingDetector
from .last_digit import LastDigitUniformityDetector
from .rounding import RoundingDetector
from .threshold import ThresholdClusteringDetector

DETECTORS: tuple[Detector, ...] = (
    ThresholdClusteringDetector(),
    RoundingDetector(),
    ArithmeticDetector(),
    DiscontinuityDetector(),
    WindowDressingDetector(),
    LastDigitUniformityDetector(),
    BalanceIdentityDetector(),
)

BY_NAME: dict[str, Detector] = {d.name: d for d in DETECTORS}

ADVISORY: frozenset[str] = frozenset(d.name for d in DETECTORS if d.advisory)
