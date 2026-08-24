"""Route modules, one per resource; `ROUTERS` is the order they appear in /docs.

  health.py       GET  /api/health
  meta.py         GET  /api/meta
  audit.py        POST /api/audit/run, GET /api/audit/latest
  banks.py        GET  /api/banks/{bank}/benford, GET /api/banks/{bank}/evidence
  submissions.py  POST/GET/DELETE /api/submissions -- uploaded reports
"""
from __future__ import annotations

from fastapi import APIRouter

from . import audit, banks, health, meta, submissions

ROUTERS: tuple[APIRouter, ...] = (
    health.router,
    meta.router,
    audit.router,
    banks.router,
    submissions.router,
)

__all__ = ["ROUTERS"]
