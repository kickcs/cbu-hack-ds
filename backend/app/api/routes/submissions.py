"""Uploaded reports: intake, queue status, results and history."""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ...submissions import UploadRejected
from ..deps import SubmissionsDep
from ..schemas import SubmissionDetailOut, SubmissionOut

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post(
    "",
    response_model=SubmissionOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a report for audit",
    response_description="The queued submission; poll it until its status leaves `queued`.",
)
async def upload(
    submissions: SubmissionsDep,
    files: list[UploadFile] = File(description="CSV, XLSX or XML, up to 25 MB each."),
) -> SubmissionOut:
    """Accept one report and put it in the queue.

    The files are stored as one isolated submission and audited on their own, against
    neither the shared dataset nor any other upload -- so a register uploaded here cannot
    change what `POST /api/audit/run` reports.

    The response comes back immediately with status `queued`: the audit is CPU-bound and
    runs on a background worker. Poll `GET /api/submissions/{id}` for `done` or `failed`.

    Rejected outright (HTTP 400) are the mistakes that are the caller's: an unsupported
    format, an empty or oversized file, too many files at once. Everything wrong *inside* a
    readable file is a finding instead, reported in `issues` next to the result.
    """
    payload = [(f.filename or "file", await f.read()) for f in files]
    try:
        return SubmissionOut.model_validate(submissions.create(payload), from_attributes=True)
    except UploadRejected as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.get(
    "",
    response_model=list[SubmissionOut],
    summary="Upload history",
    response_description="Every submission, newest first, without the per-bank results.",
)
def history(submissions: SubmissionsDep) -> list[SubmissionOut]:
    """List the uploaded reports and where each one stands.

    Results are omitted here on purpose -- the list is polled while anything is still in
    the queue, and one ranking per row would make every poll carry the whole dashboard.
    """
    return [SubmissionOut.model_validate(s, from_attributes=True) for s in submissions.list()]


@router.get(
    "/{submission_id}",
    response_model=SubmissionDetailOut,
    summary="One report with its ranking",
    response_description="The submission, its issues, and the banks it flagged.",
)
def detail(submission_id: int, submissions: SubmissionsDep) -> SubmissionDetailOut:
    """Return one submission in full.

    While the status is `queued` or `processing`, `results` is empty and `issues` holds
    only what was known at intake. Once it is `done`, `results` is the same ranking shape
    the dashboard renders for the shared dataset -- computed over this report alone, so a
    bank missing from the upload is simply absent rather than reported as clean.
    """
    submission = submissions.get(submission_id)
    if submission is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"There is no filing {submission_id:03d} in the docket.")
    return SubmissionDetailOut.model_validate(submission, from_attributes=True)


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,  # `-> None` would otherwise be documented as a 204 with a body.
    summary="Delete one report",
    response_description="Deleted; the row and the stored files are both gone.",
)
def remove(submission_id: int, submissions: SubmissionsDep) -> None:
    """Delete one report from the history, together with the files it was audited from."""
    if not submissions.delete(submission_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"There is no filing {submission_id:03d} in the docket.")


@router.delete(
    "",
    summary="Clear the history",
    response_description="How many reports were removed.",
)
def clear(submissions: SubmissionsDep) -> dict:
    """Delete every uploaded report and its files. The shared dataset is untouched."""
    return {"deleted": submissions.clear()}
