"""Domain model: what the audit pipeline produces for one bank.

These are the objects that travel between layers -- the pipeline fills them, the repository
persists them, the API serialises them through `api/schemas.py`. Pydantic models rather than
plain dataclasses, so a malformed field (a string where a MAD is expected) fails here instead
of surfacing as a broken number in the dashboard.

Kept separate from `api/schemas.py` on purpose: this is the internal shape, that one is the
published contract, and they are free to drift apart.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class BenfordResult(BaseModel):
    """Outcome of the first-digit test for one bank's loan amounts."""

    n: int = 0
    """Loan amounts that entered the test (invalid values already dropped)."""

    dropped: int = 0
    """Values rejected as non-numeric, non-finite or non-positive."""

    mad: float | None = None
    """Mean absolute deviation from the Benford shares; None when nothing was testable."""

    chi2: float | None = None
    chi2_p: float | None = None

    mad_label: str = ""
    """Nigrini's verbal reading of `mad`: close / acceptable / marginal / nonconformity."""

    sufficient: bool = True
    """False when the bank has fewer than MIN_SAMPLE rows -- no verdict is drawn (TZ §5)."""

    flagged: bool = False
    """The test fired: the sample was sufficient AND `mad` exceeded the threshold."""

    threshold: float | None = None
    """Nigrini threshold the verdict was taken against."""

    calibrated_threshold: float | None = None
    """Bootstrap threshold for this sample size, shown as a confirmation (bonus)."""


class BankAudit(BaseModel):
    """Everything the audit concluded about one bank."""

    bank: str
    benford: BenfordResult = Field(default_factory=BenfordResult)

    detector_flags: dict[str, bool] = Field(default_factory=dict)
    """Whether each detector fired, advisory ones included."""

    detector_scores: dict[str, float] = Field(default_factory=dict)
    """Each detector's score, on its own scale."""

    reason: list[str] = Field(default_factory=list)
    """Names of the tests that decided the verdict, in registry order; advisory excluded."""

    composite: float = 0.0
    """Sum of the scores of the tests in `reason` -- the ranking key."""

    suspicious: bool = False

    def primary_metric(self) -> float:
        """The single number shown next to the bank in the result CSV.

        Benford's MAD when the Benford test fired (that is the metric the spec names),
        otherwise the strongest score among the tests that did fire.
        """
        if "benford" in self.reason and self.benford.mad is not None:
            return self.benford.mad
        return max((self.detector_scores[r] for r in self.reason), default=0.0)
