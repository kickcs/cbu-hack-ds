"""A single-worker background queue for uploaded reports.

An audit over a full loan register takes seconds, not milliseconds, and it is CPU-bound
pandas work. Doing it inside the upload request would hold the connection open, hide the
progress, and let a second upload stall the first. So the request only stores the files and
returns the submission in `QUEUED`; this queue hands it to a worker thread, and the
dashboard follows the status.

One worker on purpose: two concurrent audits over the same interpreter contend for the GIL
and finish no sooner, while a serial queue gives the auditor a queue position that means
something. `Worker` is a plain thread rather than an asyncio task because the audit blocks.
"""
from __future__ import annotations

import logging
import queue
import threading
from typing import Callable

log = logging.getLogger(__name__)

_STOP = object()
"""Sentinel that ends the worker loop; `None` is not used, ids can be falsy in tests."""


class SubmissionQueue:
    """Hands submission ids to a background worker, one at a time."""

    def __init__(self, handler: Callable[[int], None]):
        self._handler = handler
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the worker; safe to call twice (the second call is a no-op)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="submission-worker", daemon=True)
        self._thread.start()
        log.info("submission queue: worker started")

    def stop(self, timeout: float = 5.0) -> None:
        """Ask the worker to finish the current item and exit."""
        if self._thread is None:
            return
        self._queue.put(_STOP)
        self._thread.join(timeout=timeout)
        self._thread = None
        log.info("submission queue: worker stopped")

    def submit(self, submission_id: int) -> None:
        self._queue.put(submission_id)

    def depth(self) -> int:
        """Items waiting, excluding the one being processed -- shown as queue position."""
        return self._queue.qsize()

    def _loop(self) -> None:
        while True:
            item = self._queue.get()
            try:
                if item is _STOP:
                    return
                self._handler(int(item))
            except Exception:  # noqa: BLE001 -- a failed submission must not kill the worker
                log.exception("submission queue: handler failed for %r", item)
            finally:
                self._queue.task_done()
