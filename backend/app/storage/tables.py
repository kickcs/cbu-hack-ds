"""Database schema as SQLAlchemy models -- five tables, bitemporal by construction (TZ §7).

Two time axes are kept as separate columns everywhere, never conflated:
- `period`      -- the reporting period the numbers describe (valid time);
- `received_at` -- when the file reached the system (transaction time).

That separation is what lets a later submission for an earlier period be stored without
overwriting anything: `raw_files` keeps every source file byte-for-byte, so a run can always
be traced back to the exact bytes it read.

Table and column names match the original hand-written schema, so a database created by an
earlier version of the backend stays readable.
"""
from __future__ import annotations

from sqlalchemy import Float, Index, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base; `Base.metadata` is what creates the schema."""


class RawFile(Base):
    """A source file exactly as it arrived -- the evidence trail behind every run."""

    __tablename__ = "raw_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    received_at: Mapped[str] = mapped_column(String, nullable=False)


class ReportLine(Base):
    """One canonical indicator value: the aggregate reports after ingestion."""

    __tablename__ = "report_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bank: Mapped[str] = mapped_column(String, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)
    indicator: Mapped[str] = mapped_column(String, nullable=False)
    tip: Mapped[str | None] = mapped_column(String)
    summa: Mapped[float] = mapped_column(Float, nullable=False)
    received_at: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (Index("idx_report_bank", "bank"),)


class AuditRun(Base):
    """One execution of the audit, with the configuration it ran under."""

    __tablename__ = "audit_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ran_at: Mapped[str] = mapped_column(String, nullable=False)
    config: Mapped[str | None] = mapped_column(Text)


class Submission(Base):
    """One uploaded report: the queue entry, and the audit it produced in isolation.

    Isolation is the reason this table exists rather than more rows in `raw_files`: a
    submission is audited against its own files only, so its verdicts can never mix with
    the shared dataset's, and deleting it removes the whole report -- rows here plus the
    directory under `Settings.upload_dir`.

    The three JSON columns hold what the dashboard reads back: the files ingested, the
    issues ingestion raised, and the ranked verdicts. They are written once, at the end of
    the run, and are small (one submission covers a few dozen banks at most).
    """

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[str | None] = mapped_column(String)
    finished_at: Mapped[str | None] = mapped_column(String)
    files_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    issues_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    result_json: Mapped[str | None] = mapped_column(Text)
    skipped_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    error: Mapped[str | None] = mapped_column(Text)
    error_key: Mapped[str | None] = mapped_column(String)
    error_params_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    total_banks: Mapped[int | None] = mapped_column(Integer)
    suspicious_count: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (Index("idx_submission_status", "status"),)


class AuditResult(Base):
    """The verdict for one bank within one run."""

    __tablename__ = "audit_results"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank: Mapped[str] = mapped_column(String, primary_key=True)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    dropped: Mapped[int | None] = mapped_column(Integer)
    mad: Mapped[float | None] = mapped_column(Float)
    chi2: Mapped[float | None] = mapped_column(Float)
    chi2_p: Mapped[float | None] = mapped_column(Float)
    mad_label: Mapped[str | None] = mapped_column(String)
    benford_flagged: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(String)
    composite: Mapped[float | None] = mapped_column(Float)
    suspicious: Mapped[int | None] = mapped_column(Integer)
