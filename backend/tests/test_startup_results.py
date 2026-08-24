"""The result files are rewritten from the dataset on disk when the API starts.

The autocheck runs `docker-compose up` and reads the result files; without startup
regeneration they would keep a previous dataset's verdicts until someone hits
`POST /api/audit/run`. This pins that behaviour.
"""
from __future__ import annotations

import os
import time

import pandas as pd

from app.api import _regenerate_results
from app.config import Settings
from app.service import AuditService
from tests import synthetic as syn


def test_startup_regenerates_result_files_for_the_dataset_on_disk(tmp_path):
    register, normativ, report, truth = syn.generate({"Clean Bank": None, "Bad Bank": "benford"}, seed=11)
    data = tmp_path / "data"
    data.mkdir(parents=True)
    register.to_csv(data / "kredit_reyestri.csv", index=False)
    normativ.to_csv(data / "normativlar.csv", index=False)
    report.to_csv(data / "hisobotlar.csv", index=False)

    settings = Settings(
        data_dir=data,
        db_path=tmp_path / "audit.db",
        upload_dir=data / ".uploads",
    )
    _regenerate_results(AuditService(settings))

    natija = data / "natija" / "shubhali_banklar.csv"
    assert natija.exists()
    frame = pd.read_csv(natija)
    expected = {b for b, reasons in truth.items() if reasons}
    assert set(frame["bank"]) == expected


def _write_dataset(data, register, normativ, report):
    register.to_csv(data / "kredit_reyestri.csv", index=False)
    normativ.to_csv(data / "normativlar.csv", index=False)
    report.to_csv(data / "hisobotlar.csv", index=False)


def test_audit_service_caches_until_the_dataset_changes(tmp_path):
    """Repeated reads must not re-audit; a touched file must force a fresh run."""
    register, normativ, report, truth = syn.generate({"Clean Bank": None, "Bad Bank": "benford"}, seed=11)
    data = tmp_path / "data"
    data.mkdir(parents=True)
    _write_dataset(data, register, normativ, report)
    service = AuditService(
        Settings(data_dir=data, db_path=tmp_path / "audit.db", upload_dir=data / ".uploads")
    )

    _, ranked = service.refresh()
    _, cached = service.refresh()
    assert cached is ranked  # same dataset on disk -> memoized, not re-run

    path = data / "kredit_reyestri.csv"
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, time.time_ns()))
    _, refreshed = service.refresh()
    assert refreshed is not ranked  # the dataset changed -> recomputed
