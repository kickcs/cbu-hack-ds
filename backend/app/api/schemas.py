"""Response contract of the audit API.

These models are what the dashboard consumes and what `/docs` documents. They mirror the
domain objects in `app/domain.py` but stay separate on purpose: the internal model is free to
change without breaking the published shape. Field descriptions here become the field
documentation in the generated OpenAPI schema.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BenfordOut(BaseModel):
    """Result of the first-digit test for one bank."""

    model_config = ConfigDict(from_attributes=True)

    n: int = Field(description="Loan amounts that entered the test.")
    dropped: int = Field(description="Values rejected as non-numeric, non-finite or non-positive.")
    mad: float | None = Field(description="Mean absolute deviation from the Benford shares.")
    chi2: float | None = Field(description="Pearson chi-square statistic.")
    chi2_p: float | None = Field(description="p-value of the chi-square goodness-of-fit test.")
    mad_label: str = Field(description="Nigrini reading of the MAD: close … nonconformity.")
    sufficient: bool = Field(description="False when the bank has fewer rows than min_sample.")
    flagged: bool = Field(description="The test fired: sample sufficient and MAD above threshold.")
    threshold: float | None = Field(default=None, description="Nigrini decision threshold.")
    calibrated_threshold: float | None = Field(
        default=None, description="Bootstrap threshold for this sample size (confirmation only)."
    )


class BankAuditOut(BaseModel):
    """Everything the audit concluded about one bank."""

    model_config = ConfigDict(from_attributes=True)

    bank: str
    suspicious: bool = Field(description="At least one deciding test fired.")
    composite: float = Field(description="Sum of the scores of the tests in `reason`.")
    reason: list[str] = Field(description="Tests that decided the verdict, advisory excluded.")
    benford: BenfordOut
    detector_flags: dict[str, bool] = Field(description="Per-detector verdict, advisory included.")
    detector_scores: dict[str, float] = Field(description="Per-detector score, each on its own scale.")


class DistributionOut(BaseModel):
    """One first digit: how often it occurs versus how often Benford expects it."""

    digit: int
    empirical: float
    theoretical: float


class BenfordDetailOut(BenfordOut):
    """The Benford result plus the distribution behind it, for charting."""

    bank: str
    distribution: list[DistributionOut] = Field(description="Digits 1..9, empirical vs theoretical.")


class EvidenceOut(BaseModel):
    """The concrete figures behind a bank's verdict, grouped per test."""

    bank: str
    reasons: list[str] = Field(description="Tests shown, deciding ones first, then advisory.")
    blocks: list[dict] = Field(
        description="One block per test: {test, title, summary, rows[]}; rows carry `suspect`."
    )


class MetaOut(BaseModel):
    """Overview of the loaded dataset and the state of the small-sample guard."""

    banks: list[str] = Field(description="Banks present in the loan register.")
    register_rows: int = Field(description="Total rows in the loan register.")
    min_sample: int = Field(description="Rows a bank needs before a register test may decide.")
    insufficient: list[str] = Field(description="Banks below that guard; no Benford verdict.")
    normativ_rows: int = Field(description="Rows of regulatory ratios.")
    report_rows: int = Field(description="Canonical indicator values parsed from the reports.")


class AuditRunSummaryOut(BaseModel):
    """What a persisted audit run produced."""

    run_id: int = Field(description="Id of the run recorded in the database.")
    total_banks: int
    suspicious_banks: list[str]
    result_file: str = Field(description="Path written in the russian spec variant.")
    natija_file: str = Field(description="Path written in the official uzbek spec variant.")
