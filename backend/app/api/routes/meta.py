"""Overview of the dataset currently on disk."""
from __future__ import annotations

from fastapi import APIRouter

from ...ingest.register import bank_column, bank_names
from ...sampling import MIN_SAMPLE, is_sample_sufficient
from ..deps import ServiceDep
from ..schemas import MetaOut

router = APIRouter(prefix="/api", tags=["dataset"])


@router.get(
    "/meta",
    response_model=MetaOut,
    summary="Dataset overview and sample-size guard",
    response_description="Banks, row counts per dataset, and the banks below the guard.",
)
def meta(service: ServiceDep) -> MetaOut:
    """Describe the loaded dataset before any test is run.

    Lists the banks found in the loan register and how many rows each dataset contributed, so
    the dashboard can tell an empty or half-parsed dataset from a healthy one.

    `insufficient` names the banks with fewer than `min_sample` loans: their Benford verdict is
    withheld rather than guessed (TZ §5), and the dashboard marks them as untestable instead of
    clean. The dataset is re-read on every call, so swapping the files on disk is enough to
    refresh this.
    """
    ctx = service.load_data()
    register = ctx.register
    return MetaOut(
        banks=bank_names(register),
        register_rows=int(len(register)),
        min_sample=MIN_SAMPLE,
        insufficient=[
            str(bank)
            for bank, rows in register.groupby(bank_column(register))
            if not is_sample_sufficient(int(len(rows)))
        ],
        normativ_rows=int(len(ctx.normativ)),
        report_rows=int(len(ctx.report)),
    )
