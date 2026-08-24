"""All persistence for an audit run behind one object.

`AuditRepository` is a context manager over a SQLAlchemy session: the domain code calls
`store_*` / `start_run` and never sees SQL or a connection. The schema is created on first
use, so a fresh checkout needs no migration step.

Everything written here is stamped with `received_at = now`, the transaction-time half of the
bitemporal model; the valid-time half (`period`) comes from the data itself. See `tables.py`.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..domain import BankAudit
from .tables import AuditResult, AuditRun, Base, RawFile, ReportLine

RAW_FILE_SUFFIXES = (".csv", ".xlsx", ".xml")
"""Source formats preserved byte-for-byte; anything else in the dataset dir is ignored."""


def now_iso() -> str:
    """Current UTC timestamp in ISO 8601 -- the `received_at` of everything written now."""
    return datetime.now(timezone.utc).isoformat()


class AuditRepository:
    """Session-scoped storage for raw files, canonical report lines and audit runs."""

    def __init__(self, db_path: str | Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{Path(db_path)}", future=True)
        Base.metadata.create_all(self._engine)
        self._session = Session(self._engine)

    def close(self) -> None:
        self._session.close()
        self._engine.dispose()

    def __enter__(self) -> "AuditRepository":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def store_raw_files(self, source_dir: str | Path) -> int:
        """Persist every source file in the dataset directory unchanged; return the count."""
        source_dir = Path(source_dir)
        received_at = now_iso()
        seen: set[str] = set()

        for path in source_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in RAW_FILE_SUFFIXES:
                continue
            relative = path.relative_to(source_dir).as_posix()
            if relative in seen:
                continue
            seen.add(relative)
            self._session.add(
                RawFile(
                    file_path=relative,
                    format=path.suffix.lstrip(".").lower(),
                    content=path.read_bytes(),
                    received_at=received_at,
                )
            )

        self._session.commit()
        return len(seen)

    def store_report_lines(self, report: pd.DataFrame) -> None:
        """Persist the canonical report model, `period` and `received_at` kept apart."""
        received_at = now_iso()
        self._session.add_all(
            ReportLine(
                bank=str(row["bank"]),
                period=str(row["period"]),
                indicator=str(row["indicator"]),
                tip=str(row.get("tip", "")),
                summa=float(row["summa"]),
                received_at=received_at,
            )
            for _, row in report.iterrows()
        )
        self._session.commit()

    def start_run(self, config: dict) -> int:
        """Open a new audit run under the given configuration; return its id."""
        run = AuditRun(ran_at=now_iso(), config=json.dumps(config, ensure_ascii=False))
        self._session.add(run)
        self._session.commit()
        return int(run.id)

    def store_audit_results(self, run_id: int, results: list[BankAudit]) -> None:
        """Persist the per-bank verdicts of one run."""
        self._session.add_all(
            AuditResult(
                run_id=run_id,
                bank=audit.bank,
                sample_size=audit.benford.n,
                dropped=audit.benford.dropped,
                mad=audit.benford.mad,
                chi2=audit.benford.chi2,
                chi2_p=audit.benford.chi2_p,
                mad_label=audit.benford.mad_label,
                benford_flagged=int(audit.benford.flagged),
                reason="|".join(audit.reason),
                composite=audit.composite,
                suspicious=int(audit.suspicious),
            )
            for audit in results
        )
        self._session.commit()
