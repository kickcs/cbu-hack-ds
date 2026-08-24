"""Persistence layer: SQLite through SQLAlchemy, bitemporal by construction (TZ §7).

  tables.py      the four tables as declarative models
  repository.py  AuditRepository -- the only object the domain code talks to
"""
from __future__ import annotations

from .repository import RAW_FILE_SUFFIXES, AuditRepository, now_iso
from .tables import AuditResult, AuditRun, Base, RawFile, ReportLine

__all__ = [
    "RAW_FILE_SUFFIXES",
    "AuditRepository",
    "AuditResult",
    "AuditRun",
    "Base",
    "RawFile",
    "ReportLine",
    "now_iso",
]
