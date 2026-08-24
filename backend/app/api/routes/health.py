"""Liveness probe."""
from __future__ import annotations

from fastapi import APIRouter

from ...sampling import MIN_SAMPLE

router = APIRouter(prefix="/api", tags=["service"])


@router.get(
    "/health",
    summary="Service liveness",
    response_description="Service status and the configured small-sample guard.",
)
def health() -> dict:
    """Report that the API is up.

    Also returns `min_sample`, the number of loan-register rows a bank must have before a
    statistical test is allowed to decide anything about it (TZ §5) -- handy as a quick check
    that the running build carries the guard at all.
    """
    return {"status": "ok", "min_sample": MIN_SAMPLE}
