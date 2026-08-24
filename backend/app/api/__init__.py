"""HTTP layer: the application factory and everything it assembles.

  deps.py    dependencies handed to the routes (the shared service, the settings)
  schemas.py the published response shapes, documented in /docs
  routes/    one module per resource

`create_app` takes the service it should serve rather than building one, so the CLI, the
tests and uvicorn all drive the same pipeline object.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import Settings
from ..service import AuditService
from ..submissions import SubmissionService
from .routes import ROUTERS

log = logging.getLogger(__name__)

API_DESCRIPTION = """
Statistical audit of a bank loan registry: Benford's law on the loan register plus seven
detectors over the aggregate reports, ranked into a list of banks worth investigating.

Read-only endpoints re-read the dataset on every call; `POST /api/audit/run` is the one that
records a run and writes the result files.

`POST /api/submissions` audits an uploaded report instead: it is queued, processed on a
background worker and kept as its own report, separate from the shared dataset.
""".strip()

TAGS_METADATA = [
    {"name": "service", "description": "Liveness and configuration."},
    {"name": "dataset", "description": "What is currently loaded from disk."},
    {"name": "audit", "description": "Running the audit and reading the ranking."},
    {"name": "banks", "description": "Drill-down into a single bank."},
    {"name": "submissions", "description": "Uploaded reports, each audited in isolation."},
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Rewrite the result files for the dataset on disk, then run the intake worker.

    The autocheck runs `docker-compose up` and reads the result files; without this step the
    files would keep the previous dataset's verdicts until someone hits `POST /api/audit/run`.
    """
    _regenerate_results(app.state.service)
    app.state.submissions.start()
    try:
        yield
    finally:
        app.state.submissions.stop()


def _regenerate_results(service: AuditService) -> None:
    """Rewrite both spec variants of the result file from the current dataset.

    A missing or malformed dataset must not stop the API -- the audit endpoint is still
    available to diagnose it, and the CLI (`make audit`) reports the reason properly.
    Running through `refresh` also warms the memo, so the first dashboard visit is fast.
    """
    try:
        ctx, ranked = service.refresh()
        service.write_result_csv(ranked)
    except Exception as exc:  # noqa: BLE001 -- a broken dataset is a finding, not a crash
        log.warning("startup: could not regenerate result files (%s) — POST /api/audit/run still can", exc)


def create_app(service: AuditService, settings: Settings) -> FastAPI:
    """Build the FastAPI application around an already-configured service."""
    app = FastAPI(
        title="RegTech Audit API",
        version="1.0.0",
        description=API_DESCRIPTION,
        openapi_tags=TAGS_METADATA,
        lifespan=lifespan,
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
    app.state.submissions = SubmissionService(settings)

    for router in ROUTERS:
        app.include_router(router)
    return app


__all__ = ["create_app"]
