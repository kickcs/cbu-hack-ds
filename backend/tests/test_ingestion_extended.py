"""Ingestion robustness: fuzzy synonym fallback and file round-trip."""
from __future__ import annotations

import numpy as np
import pandas as pd

from app import ingest
from tests import synthetic as syn


def test_fuzzy_fallback_maps_unknown_variant():
    """A novel name variant (typo/renaming not in the dictionary) still maps via the
    difflib fallback, so the day-2 closed dataset keeps working."""
    assert ingest.map_indicator("Jami  aktivlar") == "jami_aktivlar"
    assert ingest.map_indicator("KREDIT PORTFELI (BRUTTO)") == "kredit_portfeli"
    assert ingest.map_indicator("Naqd pul va MB mablaglari") == "naqd_pullar"
    # capitalization + punctuation + slight reword all resolve
    assert ingest.map_indicator("Asosiy vositalar") == "asosiy_vositalar"


def test_fuzzy_fallback_rejects_garbage():
    assert ingest.map_indicator("zzz unknown indicator 12345") is None


def test_csv_report_round_trip():
    """A generated canonical report written as CSV is ingested back losslessly."""
    import tempfile
    from pathlib import Path

    corruption = {"A": None, "B": "rounding"}
    _, _, report, _ = syn.generate(corruption, seed=9)
    # write a report-style CSV: bank_nomi/hisobot_oyi/korsatkich_nomi/turi/summa_som
    out = report.rename(
        columns={
            "bank": "bank_nomi",
            "period": "hisobot_oyi",
            "indicator": "korsatkich_nomi",
            "tip": "turi",
            "summa": "summa_som",
        }
    )
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "hisobotlar.csv"
        out.to_csv(p, index=False)
        loaded = ingest.load_aggregate_reports(d)
    assert set(loaded["indicator"]) == set(ingest.CANONICAL_INDICATORS)
    assert set(loaded["bank"]) == {"A", "B"}
    assert len(loaded) == len(report)


def test_full_file_based_pipeline(tmp_path):
    """Write register+normativ+report to disk, run the CLI-style flow end to end."""
    from app import audit

    corruption = {"X": "benford", "Y": None, "Z": "threshold", "W": "discontinuity"}
    register, normativ, report, truth = syn.generate(corruption, seed=11)

    register.to_csv(tmp_path / "kredit_reyestri.csv", index=False)
    normativ.to_csv(tmp_path / "normativlar.csv", index=False)
    rep_dir = tmp_path / "csv"
    rep_dir.mkdir()
    report.rename(columns={
        "bank": "bank_nomi", "period": "hisobot_oyi",
        "indicator": "korsatkich_nomi", "tip": "turi", "summa": "summa_som",
    }).to_csv(rep_dir / "hisobotlar.csv", index=False)

    reg2 = ingest.load_credit_register(tmp_path / "kredit_reyestri.csv")
    norm2 = ingest.load_normativ(tmp_path / "normativlar.csv")
    rep2 = ingest.load_aggregate_reports(tmp_path)

    audits = audit.audit_all(reg2, norm2, rep2)
    detected = {a.bank: set(a.reason) for a in audits if a.suspicious}
    assert set(detected) == {"X", "Z", "W"}
    assert detected["X"] == {"benford"}
    assert detected["Z"] == {"threshold"}
    assert detected["W"] == {"discontinuity"}
