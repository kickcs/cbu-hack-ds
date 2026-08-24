"""Dependencies the route handlers ask for.

The application factory puts the shared `AuditService` and `Settings` on `app.state`; routers
receive them through `Depends` instead of closing over them. That keeps every route module
importable on its own and lets a test swap the service for a stub with `dependency_overrides`.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from ..config import Settings
from ..service import AuditService


def get_service(request: Request) -> AuditService:
    """The audit pipeline shared by every request."""
    return request.app.state.service


def get_settings(request: Request) -> Settings:
    """Resolved paths of the running application."""
    return request.app.state.settings


ServiceDep = Annotated[AuditService, Depends(get_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
