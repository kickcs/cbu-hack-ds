"""Uploaded reports: the queue, the isolation of one report from the next, and deletion."""
from __future__ import annotations

import time

import pandas as pd
import pytest

from app.config import Settings
from app.ingest import iter_data_files
from app.submissions import SubmissionService, SubmissionStatus, UploadRejected
from app.submissions.model import SubmissionFile
from tests import synthetic as syn


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


@pytest.fixture
def dataset():
    """One clean bank and one with an injected Benford violation."""
    register, normativ, report, truth = syn.generate({"Clean Bank": None, "Bad Bank": "benford"}, seed=11)
    return register, normativ, report, truth


@pytest.fixture
def service(tmp_path):
    settings = Settings(
        data_dir=tmp_path / "data",
        db_path=tmp_path / "audit.db",
        upload_dir=tmp_path / "data" / ".uploads",
    )
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    service = SubmissionService(settings)
    service.start()
    yield service
    service.stop()


def wait(service: SubmissionService, submission_id: int, seconds: float = 60.0):
    """Block until the worker is done with one submission."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        submission = service.get(submission_id)
        if submission is not None and not submission.status.active:
            return submission
        time.sleep(0.05)
    raise AssertionError(f"submission {submission_id} did not finish within {seconds}s")


# -- the queue -----------------------------------------------------------------------


def test_upload_is_queued_first_and_answered_later(service, dataset):
    register, _, _, truth = dataset
    submission = service.create([("kredit_reyestri.csv", csv_bytes(register))])

    assert submission.status is SubmissionStatus.QUEUED
    assert submission.results == []

    done = wait(service, submission.id)
    assert done.status is SubmissionStatus.DONE
    assert done.finished_at is not None
    flagged = {r.bank for r in done.results if r.suspicious}
    assert flagged == {b for b, reasons in truth.items() if reasons}


def test_every_submission_keeps_its_place_in_the_history(service, dataset):
    register, _, report, _ = dataset
    first = service.create([("kredit_reyestri.csv", csv_bytes(register))])
    second = service.create([("hisobotlar.csv", csv_bytes(report))])
    wait(service, first.id)
    wait(service, second.id)

    history = service.list()
    assert [s.id for s in history] == [second.id, first.id]  # newest first
    assert all(s.status is SubmissionStatus.DONE for s in history)


# -- isolation -----------------------------------------------------------------------


def test_uploads_never_join_the_shared_dataset(service, dataset, tmp_path):
    """The dataset scan must not see an upload -- otherwise one report rewrites the audit."""
    register, _, _, _ = dataset
    submission = service.create([("kredit_reyestri.csv", csv_bytes(register))])
    wait(service, submission.id)

    stored = service.directory(submission.id) / "kredit_reyestri.csv"
    assert stored.exists()
    assert stored not in iter_data_files(tmp_path / "data")


def test_two_reports_are_audited_apart(service, dataset):
    """The same bank name in two uploads stays two separate verdicts."""
    register, _, _, _ = dataset
    clean = register[register["bank"] == "Clean Bank"]
    bad = register[register["bank"] == "Bad Bank"]

    first = wait(service, service.create([("a.csv", csv_bytes(clean))]).id)
    second = wait(service, service.create([("b.csv", csv_bytes(bad))]).id)

    assert {r.bank for r in first.results} == {"Clean Bank"}
    assert {r.bank for r in second.results} == {"Bad Bank"}
    assert not any(r.suspicious for r in first.results)


# -- partial submissions -------------------------------------------------------------


def test_tests_without_input_are_reported_as_skipped_not_as_passed(service, dataset):
    """A register alone cannot run the report detectors; saying nothing would read as clean."""
    register, _, _, _ = dataset
    done = wait(service, service.create([("kredit_reyestri.csv", csv_bytes(register))]).id)

    assert {"rounding", "arithmetic", "discontinuity", "window_dressing", "threshold"} <= set(done.skipped)
    assert any(i.code == "no_report" for i in done.issues)
    assert all("benford" not in s for s in done.skipped)


def test_report_only_submission_still_runs_its_own_detectors(service, dataset):
    register, _, report, _ = dataset
    done = wait(service, service.create([("hisobotlar.csv", csv_bytes(report))]).id)

    assert done.status is SubmissionStatus.DONE
    assert any(i.code == "no_register" for i in done.issues)
    assert all(not r.benford.sufficient for r in done.results)


# -- bad input -----------------------------------------------------------------------


def test_nothing_at_all_is_rejected(service):
    with pytest.raises(UploadRejected):
        service.create([])


@pytest.mark.parametrize(
    ("name", "data"),
    [("report.pdf", b"%PDF-1.4"), ("report.csv", b"")],
)
def test_unusable_file_is_refused_at_the_door(service, name, data):
    with pytest.raises(UploadRejected):
        service.create([(name, data)])


def test_unrecognisable_file_fails_with_a_reason_not_a_crash(service):
    done = wait(service, service.create([("junk.csv", b"a,b\n1,2\n")]).id)
    assert done.status is SubmissionStatus.FAILED
    assert done.error


def test_defects_inside_a_readable_file_become_findings(service, dataset):
    """Blank bank names do not stop the audit; they are listed next to its result."""
    register, _, _, _ = dataset
    damaged = register.copy()
    damaged.loc[damaged.index[:3], "bank"] = ""
    done = wait(service, service.create([("kredit_reyestri.csv", csv_bytes(damaged))]).id)

    assert done.status is SubmissionStatus.DONE
    assert "bank_missing" in {i.code for i in done.issues}


def test_reupload_of_the_same_bytes_is_allowed_but_noted(service, dataset):
    register, _, _, _ = dataset
    payload = csv_bytes(register)
    first = service.create([("kredit_reyestri.csv", payload)])
    wait(service, first.id)
    second = wait(service, service.create([("kredit_reyestri.csv", payload)]).id)

    assert second.status is SubmissionStatus.DONE
    assert "duplicate_submission" in {i.code for i in second.issues}


def test_reused_submission_directory_never_keeps_stale_files(service):
    """An id reused after a database reset must not inherit an earlier filing's files."""
    directory = service.directory(1)
    directory.mkdir(parents=True)
    (directory / "stale.csv").write_text("old")

    service._write_files(
        1,
        [SubmissionFile(name="fresh.csv", format="csv", size=5, sha256="x")],
        [b"fresh"],
    )

    assert not (directory / "stale.csv").exists()
    assert (directory / "fresh.csv").read_bytes() == b"fresh"


# -- deletion ------------------------------------------------------------------------


def test_deleting_a_report_takes_its_files_with_it(service, dataset):
    register, _, _, _ = dataset
    submission = service.create([("kredit_reyestri.csv", csv_bytes(register))])
    wait(service, submission.id)
    directory = service.directory(submission.id)

    assert service.delete(submission.id) is True
    assert service.get(submission.id) is None
    assert not directory.exists()
    assert service.delete(submission.id) is False


def test_clearing_the_history_leaves_nothing_behind(service, dataset, tmp_path):
    register, _, report, _ = dataset
    for name, frame in (("a.csv", register), ("b.csv", report)):
        wait(service, service.create([(name, csv_bytes(frame))]).id)

    assert service.clear() == 2
    assert service.list() == []
    assert not any((tmp_path / "data" / ".uploads").iterdir())
