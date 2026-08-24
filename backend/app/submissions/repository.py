"""Persistence for uploaded reports: the queue state and the audit each one produced.

Kept apart from `storage/repository.py` because the lifetimes differ. An audit run over the
shared dataset is an immutable record -- written once, never touched again. A submission is
mutable while it is in the queue (queued -> processing -> done) and deletable afterwards,
because the auditor owns their upload history and must be able to clear it.

Every method opens and closes its own session: the worker thread and the request handlers
touch this concurrently, and SQLite connections are not shared across threads.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from ..domain import BankAudit
from ..ingest import Issue
from ..storage.tables import Base, Submission as SubmissionRow
from .model import Submission, SubmissionFile, SubmissionStatus


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dumps(items: list) -> str:
    return json.dumps([i.model_dump(mode="json") for i in items], ensure_ascii=False)


class SubmissionRepository:
    """CRUD over the submission queue; one short-lived session per call."""

    def __init__(self, db_path: str | Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{Path(db_path)}", future=True)
        Base.metadata.create_all(self._engine)

    def create(self, title: str, files: list[SubmissionFile]) -> Submission:
        """Record a new submission in `QUEUED`; the worker picks it up from there."""
        row = SubmissionRow(
            title=title,
            status=SubmissionStatus.QUEUED,
            created_at=now_iso(),
            files_json=_dumps(files),
        )
        with Session(self._engine) as session:
            session.add(row)
            session.commit()
            return _to_model(row, with_results=False)

    def list(self) -> list[Submission]:
        """Every submission, newest first, without the per-bank results."""
        with Session(self._engine) as session:
            rows = session.scalars(select(SubmissionRow).order_by(SubmissionRow.id.desc())).all()
            return [_to_model(r, with_results=False) for r in rows]

    def get(self, submission_id: int, *, with_results: bool = True) -> Submission | None:
        with Session(self._engine) as session:
            row = session.get(SubmissionRow, submission_id)
            return _to_model(row, with_results=with_results) if row else None

    def set_issues(self, submission_id: int, issues: list[Issue]) -> None:
        """Attach issues known before the run -- the worker uses them as its seed."""
        self._update(submission_id, issues_json=_dumps(issues))

    def mark_processing(self, submission_id: int) -> None:
        self._update(submission_id, status=SubmissionStatus.PROCESSING, started_at=now_iso())

    def mark_done(
        self,
        submission_id: int,
        *,
        files: list[SubmissionFile],
        issues: list[Issue],
        skipped: list[str],
        results: list[BankAudit],
    ) -> None:
        """Close a submission with everything the run produced."""
        self._update(
            submission_id,
            status=SubmissionStatus.DONE,
            finished_at=now_iso(),
            files_json=_dumps(files),
            issues_json=_dumps(issues),
            skipped_json=json.dumps(skipped, ensure_ascii=False),
            result_json=_dumps(results),
            total_banks=len(results),
            suspicious_count=sum(1 for r in results if r.suspicious),
        )

    def mark_failed(
        self,
        submission_id: int,
        error: str,
        issues: list[Issue] | None = None,
        *,
        error_key: str | None = None,
        error_params: dict[str, str | int] | None = None,
    ) -> None:
        self._update(
            submission_id,
            status=SubmissionStatus.FAILED,
            finished_at=now_iso(),
            error=error,
            error_key=error_key,
            error_params_json=json.dumps(error_params or {}, ensure_ascii=False),
            issues_json=_dumps(issues or []),
        )

    def delete(self, submission_id: int) -> bool:
        with Session(self._engine) as session:
            row = session.get(SubmissionRow, submission_id)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    def clear(self) -> list[int]:
        """Drop the whole history; returns the ids removed so their files can follow."""
        with Session(self._engine) as session:
            ids = list(session.scalars(select(SubmissionRow.id)).all())
            session.execute(delete(SubmissionRow))
            session.commit()
            return [int(i) for i in ids]

    def interrupted(self) -> list[int]:
        """Ids left mid-flight by a restart: `PROCESSING` rows nobody is working on."""
        with Session(self._engine) as session:
            return [
                int(i)
                for i in session.scalars(
                    select(SubmissionRow.id).where(SubmissionRow.status == SubmissionStatus.PROCESSING)
                ).all()
            ]

    def pending(self) -> list[int]:
        """Ids still queued -- re-enqueued on startup so a restart does not lose them."""
        with Session(self._engine) as session:
            return [
                int(i)
                for i in session.scalars(
                    select(SubmissionRow.id)
                    .where(SubmissionRow.status == SubmissionStatus.QUEUED)
                    .order_by(SubmissionRow.id)
                ).all()
            ]

    def _update(self, submission_id: int, **fields) -> None:
        with Session(self._engine) as session:
            row = session.get(SubmissionRow, submission_id)
            if row is None:
                return
            for key, value in fields.items():
                setattr(row, key, value)
            session.commit()


def _to_model(row: SubmissionRow, *, with_results: bool) -> Submission:
    """One database row as the domain object; results are heavy, so they are opt-in."""
    return Submission(
        id=int(row.id),
        title=row.title,
        status=SubmissionStatus(row.status),
        created_at=row.created_at,
        started_at=row.started_at,
        finished_at=row.finished_at,
        files=[SubmissionFile(**f) for f in json.loads(row.files_json or "[]")],
        issues=[Issue(**i) for i in json.loads(row.issues_json or "[]")],
        skipped=json.loads(row.skipped_json or "[]"),
        error=row.error,
        error_key=row.error_key,
        error_params=json.loads(row.error_params_json or "{}"),
        total_banks=row.total_banks,
        suspicious_count=row.suspicious_count,
        results=(
            [BankAudit(**a) for a in json.loads(row.result_json or "[]")] if with_results else []
        ),
    )
