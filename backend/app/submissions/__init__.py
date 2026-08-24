"""Uploaded reports: one submission = one set of files = one isolated audit.

  model.py       what a submission is and the four states it moves through
  queue.py       the single background worker the upload request hands off to
  runner.py      auditing one submission's directory, partial datasets included
  repository.py  the queue state and the verdicts, in SQLite
  service.py     intake, retrieval and deletion -- the object the API talks to

The isolation is structural, not conventional: files land in their own directory under
`Settings.upload_dir`, which `ingest.iter_data_files` skips, so an uploaded register can
never alter what the shared dataset audit sees.
"""
from __future__ import annotations

from .model import Submission, SubmissionFile, SubmissionStatus
from .queue import SubmissionQueue
from .repository import SubmissionRepository
from .runner import SubmissionError, SubmissionRun, audit_submission
from .service import SubmissionService, UploadRejected

__all__ = [
    "Submission",
    "SubmissionError",
    "SubmissionFile",
    "SubmissionQueue",
    "SubmissionRepository",
    "SubmissionRun",
    "SubmissionService",
    "SubmissionStatus",
    "UploadRejected",
    "audit_submission",
]
