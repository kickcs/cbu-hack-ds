"""Running the audit and reading its ranked results."""
from __future__ import annotations

from fastapi import APIRouter

from ..deps import ServiceDep, SettingsDep
from ..schemas import AuditRunSummaryOut, BankAuditOut

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.post(
    "/run",
    response_model=AuditRunSummaryOut,
    summary="Run the audit and record it",
    response_description="Run id, the suspicious banks, and the two result files written.",
)
def run_audit(service: ServiceDep, settings: SettingsDep) -> AuditRunSummaryOut:
    """Execute the full audit and persist everything it touched.

    Runs the Benford test and all detectors over the dataset currently on disk, then records
    the run: the source files byte-for-byte, the canonical report lines, and the per-bank
    verdicts, each stamped with its ingestion time alongside its reporting period (TZ §7).

    Finally the suspicious banks are written to both spec variants of the result file --
    `результат/подозрительные_банки.csv` and `natija/shubhali_banklar.csv` -- with identical
    rows under different column names. This is the endpoint that produces the deliverable;
    use `GET /api/audit/latest` to look at results without writing anything.
    """
    ctx = service.refresh()[0]
    ranked = service.refresh()[1]
    run_id = service.persist_run(ctx, ranked)
    service.write_result_csv(ranked)
    return AuditRunSummaryOut(
        run_id=run_id,
        total_banks=len(ranked),
        suspicious_banks=[a.bank for a in ranked if a.suspicious],
        result_file=str(settings.result_path),
        natija_file=str(settings.natija_path),
    )


@router.get(
    "/latest",
    response_model=list[BankAuditOut],
    summary="Ranked audit results",
    response_description="Every bank, most suspicious first, with per-test detail.",
)
def latest(service: ServiceDep) -> list[BankAuditOut]:
    """Audit the current dataset and return the ranking, writing nothing.

    Every bank is returned, not just the suspicious ones, so the dashboard can show the clean
    ones as evidence that the tests discriminate. Banks are ordered by composite score --
    the sum of the scores of the tests that fired -- and ties are broken by name.

    Each entry carries the full Benford result plus every detector's flag and score, advisory
    detectors included; `reason` lists only the tests that actually decided the verdict.
    """
    return service.refresh()[1]
