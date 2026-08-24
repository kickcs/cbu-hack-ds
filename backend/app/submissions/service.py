"""The upload side of the audit: accept files, queue them, serve and delete the history.

This is the only object that touches all three pieces -- the directory on disk, the row in
the database and the worker queue -- so the invariant they share lives in one place: a
submission's files, its row and its place in the queue are created together and destroyed
together. Deleting a report leaves nothing behind.

Uploads are written under `Settings.upload_dir`, a dot-directory that the dataset scan
skips (`ingest.iter_data_files`). That is what keeps a submitted file out of the shared
dataset: uploading a register cannot change what `POST /api/audit/run` sees.
"""
from __future__ import annotations

import hashlib
import logging
import shutil
from pathlib import Path

from ..config import Settings
from ..ingest import MAX_FILES, check_upload, safe_name
from ..ingest.issues import Issue, warning
from .model import Submission, SubmissionFile, SubmissionStatus
from .queue import SubmissionQueue
from .repository import SubmissionRepository
from .runner import SubmissionError, audit_submission

log = logging.getLogger(__name__)


class UploadRejected(ValueError):
    """The upload cannot be accepted at all; the message goes back as HTTP 400."""


class SubmissionService:
    """Uploaded reports: intake, queue, retrieval, deletion."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._repo = SubmissionRepository(settings.db_path)
        self._queue = SubmissionQueue(self.process)

    # -- lifecycle -------------------------------------------------------------------

    def start(self) -> None:
        """Start the worker and recover whatever the last shutdown interrupted."""
        self._queue.start()
        for submission_id in self._repo.interrupted():
            self._repo.mark_failed(
                submission_id,
                "The service restarted while this filing was being examined — upload it again.",
            )
        for submission_id in self._repo.pending():
            self._queue.submit(submission_id)

    def stop(self) -> None:
        self._queue.stop()

    # -- intake ----------------------------------------------------------------------

    def create(self, uploads: list[tuple[str, bytes]]) -> Submission:
        """Store the files as one report and queue it. Raises `UploadRejected` on bad input."""
        if not uploads:
            raise UploadRejected("Choose at least one file to upload.")
        if len(uploads) > MAX_FILES:
            raise UploadRejected(f"One filing holds at most {MAX_FILES} files.")

        rejections = [i.message for name, data in uploads for i in check_upload(name, len(data))]
        if rejections:
            raise UploadRejected(" ".join(dict.fromkeys(rejections)))

        files = [
            SubmissionFile(
                name=safe_name(name),
                format=Path(name).suffix.lstrip(".").lower(),
                size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
            )
            for name, data in uploads
        ]
        submission = self._repo.create(title=_title(files), files=files)

        try:
            self._write_files(submission.id, files, [data for _, data in uploads])
        except OSError as exc:
            log.exception("submission %s: cannot store files", submission.id)
            self._repo.mark_failed(submission.id, f"The files could not be stored: {exc}")
            return self._repo.get(submission.id) or submission

        duplicate = self._duplicate_note(submission.id, files)
        if duplicate is not None:
            # Recorded before queueing so the worker picks it up as the seed of the run's
            # issue list -- a re-upload is allowed, it just says so.
            submission.issues = [duplicate]
            self._repo.set_issues(submission.id, submission.issues)

        self._queue.submit(submission.id)
        return submission

    # -- reading ---------------------------------------------------------------------

    def list(self) -> list[Submission]:
        return self._repo.list()

    def get(self, submission_id: int) -> Submission | None:
        return self._repo.get(submission_id)

    def queue_depth(self) -> int:
        return self._queue.depth()

    # -- deletion --------------------------------------------------------------------

    def delete(self, submission_id: int) -> bool:
        """Remove one report: its row and its files."""
        if not self._repo.delete(submission_id):
            return False
        shutil.rmtree(self.directory(submission_id), ignore_errors=True)
        return True

    def clear(self) -> int:
        """Remove the whole history."""
        removed = self._repo.clear()
        for submission_id in removed:
            shutil.rmtree(self.directory(submission_id), ignore_errors=True)
        return len(removed)

    # -- worker ----------------------------------------------------------------------

    def process(self, submission_id: int) -> None:
        """Audit one submission. Runs on the worker thread; never raises."""
        submission = self._repo.get(submission_id, with_results=False)
        if submission is None or submission.status is not SubmissionStatus.QUEUED:
            return
        self._repo.mark_processing(submission_id)
        seed = list(submission.issues)
        try:
            run = audit_submission(self.directory(submission_id), submission.files)
        except SubmissionError as exc:
            self._repo.mark_failed(submission_id, str(exc), seed)
        except Exception as exc:  # noqa: BLE001 -- an unreadable upload is not a server fault
            log.exception("submission %s failed", submission_id)
            self._repo.mark_failed(submission_id, f"The examination stopped on an error: {exc}", seed)
        else:
            self._repo.mark_done(
                submission_id,
                files=run.files,
                issues=seed + run.issues,
                skipped=run.skipped,
                results=run.results,
            )

    # -- paths -----------------------------------------------------------------------

    def directory(self, submission_id: int) -> Path:
        """Where one submission's files live -- one directory per report, never shared."""
        return self._settings.upload_dir / str(submission_id)

    def _write_files(self, submission_id: int, files: list[SubmissionFile], blobs: list[bytes]) -> None:
        directory = self.directory(submission_id)
        # A submission id can be reused after the database is reset; without this wipe the
        # stale files of an earlier filing would leak into the audit of the new one.
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)
        for meta, data in zip(files, blobs):
            (directory / meta.name).write_bytes(data)

    def _duplicate_note(self, submission_id: int, files: list[SubmissionFile]) -> Issue | None:
        """Warn when the same bytes were already submitted, without blocking the re-run."""
        digests = {f.sha256 for f in files}
        for other in self._repo.list():
            if other.id == submission_id:
                continue
            if digests & {f.sha256 for f in other.files}:
                return warning(
                    "duplicate_submission",
                    f"The same file was filed before, as filing {other.id:03d} on {other.created_at[:10]}.",
                )
        return None


def _title(files: list[SubmissionFile]) -> str:
    """Human name of the report: the file it came in, plus how many joined it."""
    head = files[0].name
    return head if len(files) == 1 else f"{head} +{len(files) - 1}"
