"""The audit holds up on a fresh production-like dataset: precision/recall == 1.0.

The day-2 autocheck runs against a closed dataset in the same shape but with other bank
names and values. `tests/day2.py` reproduces that (fresh bank universe, reports split
across csv/xlsx/xml with raw indicator labels); this test proves the file-based pipeline
-- not just the canonical DataFrames -- still finds exactly the injected violations and
maps every indicator label.
"""
from __future__ import annotations

import pytest

from app import audit, ingest
from app.config import Settings
from app.service import AuditService
from tests import day2


def _detect(ranked):
    return {a.bank: set(a.reason) for a in ranked if a.suspicious}


def _score(ranked, truth):
    detected = _detect(ranked)
    expected = {b for b, reasons in truth.items() if reasons}
    tp = len(expected & detected.keys())
    fp = len(set(detected) - expected)
    fn = sum(1 for b in expected if b not in detected or not (truth[b] & detected[b]))
    return tp, fp, fn, len(expected)


@pytest.mark.parametrize("seed", range(5))
def test_day2_file_pipeline_is_exact(tmp_path, seed):
    """Across seeds, a fresh production-like dataset yields perfect precision/recall."""
    truth = day2.build(tmp_path / "data", seed=seed)
    settings = Settings(
        data_dir=tmp_path / "data",
        db_path=tmp_path / "audit.db",
        upload_dir=tmp_path / "data" / ".uploads",
    )
    ranked = AuditService(settings).run_ranked(AuditService(settings).load_data())
    tp, fp, fn, total = _score(ranked, truth)
    assert tp == total and fp == 0 and fn == 0, f"tp={tp} fp={fp} fn={fn} total={total}"


def test_day2_maps_every_raw_indicator_label(tmp_path):
    day2.build(tmp_path / "data", seed=1)
    before = ingest.unknown_indicator_count()
    report = ingest.load_aggregate_reports(tmp_path / "data")
    assert set(report["indicator"]) == set(ingest.CANONICAL_INDICATORS)
    assert ingest.unknown_indicator_count() == before
    assert len(report["bank"].unique()) == len(day2.BANKS)


def test_day2_clean_banks_never_flagged(tmp_path):
    day2.build(tmp_path / "data", seed=2)
    settings = Settings(data_dir=tmp_path / "data", db_path=tmp_path / "audit.db")
    ranked = AuditService(settings).run_ranked(AuditService(settings).load_data())
    flagged = {a.bank for a in ranked if a.suspicious}
    assert flagged == set(day2.VIOLATIONS)
