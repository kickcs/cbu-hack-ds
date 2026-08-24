"""Drill-down into a single bank: its first-digit distribution and its evidence."""
from __future__ import annotations

from fastapi import APIRouter

from ... import benford
from ...audit import evidence as evidence_module
from ...audit import run_benford
from ...ingest.register import loan_amounts
from ..deps import ServiceDep
from ..schemas import BenfordDetailOut, DistributionOut, EvidenceOut

router = APIRouter(prefix="/api/banks", tags=["banks"])


@router.get(
    "/{bank}/benford",
    response_model=BenfordDetailOut,
    summary="First-digit distribution for one bank",
    response_description="Benford metrics plus the empirical and theoretical shares per digit.",
)
def benford_detail(bank: str, service: ServiceDep) -> BenfordDetailOut:
    """Return the Benford test for one bank together with the distribution behind it.

    The bank name is matched case-insensitively. The test runs over that bank's loan amounts
    in the register -- never over the aggregate report, which is far too small to test.

    On top of the metrics served by `/api/audit/latest`, the response carries the observed and
    theoretical share of each leading digit 1..9, which is what the dashboard charts. A bank
    below the sample guard still gets its distribution back, with `sufficient=false` marking
    the verdict as withheld. An unknown bank yields an empty sample (`n=0`), not an error.
    """
    ctx = service.refresh()[0]
    values = loan_amounts(ctx.register, bank, exact=False)

    result = run_benford(values)
    digits, _ = benford.extract_first_digits(values)
    observed = benford.empirical_distribution(digits)
    theoretical = benford.benford_probabilities()

    return BenfordDetailOut(
        bank=bank,
        **result.model_dump(),
        distribution=[
            DistributionOut(
                digit=digit,
                empirical=round(float(observed[i]), 4),
                theoretical=round(theoretical[digit], 4),
            )
            for i, digit in enumerate(benford.FIRST_DIGITS)
        ],
    )


@router.get(
    "/{bank}/evidence",
    response_model=EvidenceOut,
    summary="Evidence behind one bank's verdict",
    response_description="One block per test that fired, each with the rows an auditor reads.",
)
def bank_evidence(bank: str, service: ServiceDep) -> EvidenceOut:
    """Return the concrete figures that made each test fire for this bank.

    Every test explains itself: the periods, values and deviations it reacted to, with the
    offending rows marked `suspect`. This is what turns a score into something an auditor can
    check by hand.

    Deciding tests come first, then the advisory ones (last-digit uniformity, balance
    identity) -- they are shown because they are informative, even though they never affect
    the verdict. A bank that triggered nothing, or a name that matches none, comes back with
    empty lists rather than a 404.
    """
    ctx, ranked = service.refresh()
    target = next((a for a in ranked if a.bank.lower() == bank.lower()), None)
    if target is None:
        return EvidenceOut(bank=bank, reasons=[], blocks=[])

    shown = target.reason + [
        name
        for name, fired in target.detector_flags.items()
        if fired and name not in target.reason
    ]
    blocks = evidence_module.collect_evidence(
        target.bank, shown, ctx.register, ctx.normativ, ctx.report
    )
    return EvidenceOut(bank=target.bank, reasons=shown, blocks=blocks)
