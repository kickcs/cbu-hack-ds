"""Route modules, one per resource; `ROUTERS` is the order they appear in /docs.

  health.py  GET  /api/health
  meta.py    GET  /api/meta
  audit.py   POST /api/audit/run, GET /api/audit/latest
  banks.py   GET  /api/banks/{bank}/benford, GET /api/banks/{bank}/evidence
"""
from __future__ import annotations

from fastapi import APIRouter

from . import audit, banks, health, meta

ROUTERS: tuple[APIRouter, ...] = (
    health.router,
    meta.router,
    audit.router,
    banks.router,
)

__all__ = ["ROUTERS"]
