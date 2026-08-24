"""Detector tests: synthetic edge cases plus a self-check against the sample answer
key (kept out of the production code path -- this test only documents expected
behaviour on the provided sample)."""
from __future__ import annotations

import pandas as pd
import pytest

from app import audit, detectors as det, ingest

DATA = None


@pytest.fixture(scope="module")
def sample_data():
    data = ingest  # noqa
    return {
        "register": data.load_credit_register("kredit_reyestri.csv"),
        "normativ": data.load_normativ("normativlar.csv"),
        "report": data.load_aggregate_reports("."),
    }


def test_threshold_detects_clustering_above_limit():
    norm = pd.DataFrame(
        {
            "bank": ["A"] * 6 + ["B"] * 6,
            "k1_kapital_yetarliligi": [0.132, 0.133, 0.134, 0.131, 0.1335, 0.1305] * 2,
            "chegara_k1": [0.13] * 12,
        }
    )
    rows = det.detect_threshold(norm)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and flags["B"]


def test_threshold_ignores_spread_out_k1():
    norm = pd.DataFrame(
        {"bank": ["C"] * 6, "k1_kapital_yetarliligi": [0.131, 0.15, 0.17, 0.19, 0.20, 0.22],
         "chegara_k1": [0.13] * 6}
    )
    rows = det.detect_threshold(norm)
    assert not bool(rows.loc[rows["bank"] == "C", "flagged"].iloc[0])


def test_rounding_detects_rounded_values():
    report = pd.DataFrame(
        {
            "bank": ["A"] * 6 + ["B"] * 6,
            "period": ["2025-10"] * 12,
            "indicator": ["x"] * 12,
            "tip": ["aktiv"] * 12,
            "summa": [20_000_000, 31_000_000, 42_000_000, 10_000_000, 5_000_000, 90_000_000]
            + [1_234_567] * 6,
        }
    )
    rows = det.detect_rounding(report)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_arithmetic_detects_jami_component_mismatch():
    report = pd.DataFrame(
        {
            "bank": ["A"] * 4 + ["B"] * 4,
            "period": ["2026-01"] * 8,
            "indicator": ["kredit_portfeli", "kredit_zaxirasi", "jami_aktivlar", "jami_passivlar"] * 2,
            "tip": ["aktiv", "aktiv", "aktiv", "passiv"] * 2,
            "summa": [100, -10, 100, 90, 100, -10, 90, 90],  # A inconsistent, B consistent
        }
    )
    rows = det.detect_arithmetic(report)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_discontinuity_detects_mid_series_jump():
    report = pd.DataFrame(
        {
            "bank": ["A"] * 6 + ["B"] * 6,
            "period": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"] * 2,
            "indicator": ["jami_aktivlar"] * 12,
            "tip": ["aktiv"] * 12,
            "summa": [100, 101, 102, 103, 150, 151] + [100, 101, 102, 103, 104, 105],
        }
    )
    rows = det.detect_discontinuity(report)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_window_dressing_detects_last_period_jump():
    report = pd.DataFrame(
        {
            "bank": ["A"] * 6 + ["B"] * 6,
            "period": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"] * 2,
            "indicator": ["jami_aktivlar"] * 12,
            "tip": ["aktiv"] * 12,
            "summa": [100, 101, 102, 103, 104, 150] + [100, 101, 102, 103, 104, 105],
        }
    )
    rows = det.detect_window_dressing(report)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_last_digit_detects_rounded_amounts():
    register = pd.DataFrame(
        {
            "bank": ["A"] * 400 + ["B"] * 400,
            "summa": [1_000_000 + i * 10 for i in range(400)]  # A: every amount ends in 0
            + [1_000_000 + i for i in range(400)],  # B: last digits cycle 0-9 uniformly
        }
    )
    rows = det.detect_last_digit(register)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_last_digit_respects_sample_guard():
    register = pd.DataFrame({"bank": ["C"] * 100, "summa": [10 * i for i in range(100)]})
    rows = det.detect_last_digit(register)
    row = rows.loc[rows["bank"] == "C"].iloc[0]
    assert not bool(row["flagged"]) and row["score"] == 0.0


def test_balance_detects_identity_violation():
    report = pd.DataFrame(
        {
            "bank": ["A"] * 2 + ["B"] * 2,
            "period": ["2026-01"] * 4,
            "indicator": ["jami_aktivlar", "jami_passivlar"] * 2,
            "tip": ["aktiv", "passiv"] * 2,
            "summa": [100.0, 90.0, 100.0, 100.0],  # A breaks the identity, B holds it
        }
    )
    rows = det.detect_balance(report)
    flags = dict(zip(rows["bank"], rows["flagged"]))
    assert flags["A"] and not flags["B"]


def test_advisory_detectors_stay_out_of_reason(sample_data):
    audits = audit.audit_all(
        sample_data["register"], sample_data["normativ"], sample_data["report"]
    )
    assert det.ADVISORY == {"last_digit", "balance"}
    for a in audits:
        assert set(a.reason).isdisjoint(det.ADVISORY)
        assert det.ADVISORY <= set(a.detector_flags)


def test_result_frame_supports_both_tz_column_sets(sample_data):
    audits = audit.audit_all(
        sample_data["register"], sample_data["normativ"], sample_data["report"]
    )
    ru = audit.to_suspicious_frame(audits)
    uz = audit.to_suspicious_frame(audits, audit.NATIJA_COLUMNS)
    assert list(ru.columns) == ["банк", "значение_mad", "причина"]
    assert list(uz.columns) == ["bank", "mad_qiymati", "sabab"]
    assert ru.values.tolist() == uz.values.tolist()
    assert len(ru) > 0


def test_ingestion_maps_all_observed_synonyms():
    report = ingest.load_aggregate_reports(".")
    assert ingest.unknown_indicator_count() == 0
    assert set(report["indicator"]) == set(ingest.CANONICAL_INDICATORS)


def test_ingestion_aggregate_is_bitemporal_friendly():
    report = ingest.load_aggregate_reports(".")
    assert "period" in report.columns
    assert len(report["bank"].unique()) == 13
