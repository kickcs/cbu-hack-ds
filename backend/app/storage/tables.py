"""Database schema as SQLAlchemy models -- four tables, bitemporal by construction (TZ §7).

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
