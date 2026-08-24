"""The audit pipeline as one object, shared by the API and the CLI.

`AuditService` is the only place that knows the order of operations -- load, audit, rank,
persist, write -- so the two entry points cannot drift apart. It holds no state between
calls: the dataset is re-read on every request, because the day-2 dataset may be swapped on
disk while the service is running.
"""
from __future__ import annotations

import pandas as pd

from . import audit, ingest
from .config import Settings
from .detectors import AuditContext
from .domain import BankAudit
from .storage import AuditRepository


class AuditService:
    """Load the datasets, run the audit, persist and export the results."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def settings(self) -> Settings:
        return self._settings

    def load_data(self) -> AuditContext:
        """Read the three datasets fresh: loan register, regulatory ratios, reports."""
        data_dir = self._settings.data_dir
        return AuditContext(
            register=ingest.load_credit_register(data_dir / "kredit_reyestri.csv"),
            normativ=ingest.load_normativ(data_dir / "normativlar.csv"),
            report=ingest.load_aggregate_reports(data_dir),
        )

    def run_ranked(self, ctx: AuditContext) -> list[BankAudit]:
        """Run every test over every bank, most suspicious first."""
        return audit.rank_banks(audit.audit_all(ctx.register, ctx.normativ, ctx.report))

    def write_result_csv(self, ranked: list[BankAudit]) -> pd.DataFrame:
        """Write the suspicious banks to both spec variants of the result file."""
        frame = audit.to_suspicious_frame([a for a in ranked if a.suspicious])
        natija = frame.set_axis(list(audit.NATIJA_COLUMNS), axis="columns")
        for path, out_frame in (
            (self._settings.result_path, frame),
            (self._settings.natija_path, natija),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            out_frame.to_csv(path, index=False)
        return frame

    def persist_run(self, ctx: AuditContext, ranked: list[BankAudit]) -> int:
        """Store raw files, canonical report lines and verdicts; return the run id."""
        with AuditRepository(self._settings.db_path) as repo:
            repo.store_raw_files(self._settings.data_dir)
            repo.store_report_lines(ctx.report)
            run_id = repo.start_run({"mad_threshold": audit.BENFORD_THRESHOLD})
            repo.store_audit_results(run_id, ranked)
        return run_id
