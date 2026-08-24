"""ASGI entry point: `uvicorn app.main:app`.

Everything else lives elsewhere -- the routes in `app/api/routes/`, the pipeline in
`app/service.py`. This module only wires the two together for the server process; the CLI
(`cli.py`) builds the same service without any of the HTTP layer.
"""
from __future__ import annotations

import logging
import sys

from .api import create_app
from .config import Settings
from .service import AuditService

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

settings = Settings.from_env()
app = create_app(AuditService(settings), settings)
