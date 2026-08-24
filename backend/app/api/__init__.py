"""HTTP layer: the application factory and everything it assembles.

  deps.py    dependencies handed to the routes (the shared service, the settings)
  schemas.py the published response shapes, documented in /docs
  routes/    one module per resource

`create_app` takes the service it should serve rather than building one, so the CLI, the
tests and uvicorn all drive the same pipeline object.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import Settings
from ..service import AuditService
from .routes import ROUTERS

API_DESCRIPTION = """
Statistical audit of a bank loan registry: Benford's law on the loan register plus seven
detectors over the aggregate reports, ranked into a list of banks worth investigating.

Read-only endpoints re-read the dataset on every call; `POST /api/audit/run` is the one that
records a run and writes the result files.
""".strip()

TAGS_METADATA = [
    {"name": "service", "description": "Liveness and configuration."},
    {"name": "dataset", "description": "What is currently loaded from disk."},
    {"name": "audit", "description": "Running the audit and reading the ranking."},
    {"name": "banks", "description": "Drill-down into a single bank."},
]


def create_app(service: AuditService, settings: Settings) -> FastAPI:
    """Build the FastAPI application around an already-configured service."""
    app = FastAPI(
        title="RegTech Audit API",
        version="1.0.0",
        description=API_DESCRIPTION,
        openapi_tags=TAGS_METADATA,
    )
    # The dashboard is served from a different origin (:5173 in dev, nginx in Docker).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handed to the routes through app/api/deps.py.
    app.state.service = service
    app.state.settings = settings

    for router in ROUTERS:
        app.include_router(router)
    return app


__all__ = ["create_app"]
