"""Per-bank evidence: the concrete figures behind each verdict, for the dashboard.

Every detector produces its own evidence block (`detectors/base.py`), so this module only
adds the Benford block -- the Benford test lives outside the detector registry -- and
dispatches each reason to whoever can explain it.
"""
from __future__ import annotations

import pandas as pd

from .. import benford
from ..detectors import BY_NAME, AuditContext, EvidenceBlock
from ..ingest.register import loan_amounts
from .pipeline import BENFORD_REASON

_SUSPECT_DIGIT_DEVIATION = 0.05
"""Deviation from the theoretical share that marks a digit as worth looking at."""


def benford_evidence(register: pd.DataFrame, bank: str) -> EvidenceBlock:
    """Empirical vs theoretical share of every first digit, worst deviation first."""
    digits, _ = benford.extract_first_digits(loan_amounts(register, bank))
    observed = benford.empirical_distribution(digits)
    theoretical = benford.benford_probabilities()

    rows = []
    for i, digit in enumerate(benford.FIRST_DIGITS):
        deviation = float(observed[i] - theoretical[digit])
        rows.append(
            {
                "digit": int(digit),
                "observed": round(float(observed[i]), 4),
                "expected": round(theoretical[digit], 4),
                "deviation": round(deviation, 4),
                "suspect": abs(deviation) > _SUSPECT_DIGIT_DEVIATION,
            }
        )
    rows.sort(key=lambda r: -abs(r["deviation"]))

    worst = rows[0]
    return {
        "test": BENFORD_REASON,
        "title": "Departure from Benford's law",
        "summary": f"Digit {worst['digit']} leads {worst['observed']:.1%} of amounts "
        f"instead of {worst['expected']:.1%}, a deviation of {worst['deviation']:+.1%}.",
        "rows": rows,
    }


def collect_evidence(
    bank: str,
    reasons: list[str],
    register: pd.DataFrame,
    normativ: pd.DataFrame,
    report: pd.DataFrame,
) -> list[EvidenceBlock]:
    """One evidence block per reason the bank triggered, in the order given."""
    ctx = AuditContext(register=register, normativ=normativ, report=report)
    blocks: list[EvidenceBlock] = []
    for reason in reasons:
        if reason == BENFORD_REASON:
            blocks.append(benford_evidence(register, bank))
        elif reason in BY_NAME:
            blocks.append(BY_NAME[reason].evidence(ctx, bank))
    return blocks
