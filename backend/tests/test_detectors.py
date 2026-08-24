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
    """A's total overstates its components; B's foots. Both carry the full component set,
    which is what the detector requires before it will judge a period."""
    components = [
        ("naqd_pullar", 20.0),
        ("banklararo_joylashtirishlar", 20.0),
        ("kredit_portfeli", 30.0),
        ("kredit_zaxirasi", -10.0),
        ("qimmatli_qogozlar", 15.0),
        ("asosiy_vositalar", 15.0),
    ]  # sums to 90
    rows = []
    for bank, total in (("A", 100.0), ("B", 90.0)):
        for indicator, value in components:
            rows.append({"bank": bank, "period": "2026-01", "indicator": indicator,
                         "tip": "aktiv", "summa": value})
        rows.append({"bank": bank, "period": "2026-01", "indicator": "jami_aktivlar",
                     "tip": "aktiv", "summa": total})
        rows.append({"bank": bank, "period": "2026-01", "indicator": "jami_passivlar",
                     "tip": "passiv", "summa": 90.0})

    result = det.detect_arithmetic(pd.DataFrame(rows))
    flags = dict(zip(result["bank"], result["flagged"]))
    assert flags["A"] and not flags["B"]


PERIODS = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]

_ASSET_COMPONENTS = (
    "naqd_pullar",
    "banklararo_joylashtirishlar",
    "kredit_portfeli",
    "kredit_zaxirasi",
    "qimmatli_qogozlar",
    "asosiy_vositalar",
)
_PASSIVE_LINES = (
    "depozitlar_aholi",
    "depozitlar_yuridik",
    "banklararo_qarzlar",
    "chiqarilgan_qimmatli_qogozlar",
)


def build_report(bank: str, totals: list[float], spike_lines: tuple[str, ...] | None = None,
                 spike_period: str | None = None, spike_factor: float = 1.0) -> pd.DataFrame:
    """Report where every line tracks the total, except named lines in one period.

    `spike_lines=None` makes every line move with the total -- a level shift. Naming a
    couple of lines and a factor concentrates the move in them, leaving the rest flat.
    """
    rows = []
    for period, total in zip(PERIODS, totals):
        base = totals[0]
        for indicator in _ASSET_COMPONENTS + _PASSIVE_LINES:
            if spike_lines is None:
                value = total / 6
            elif indicator in spike_lines and period == spike_period:
                value = base / 6 * spike_factor
            else:
                value = base / 6
            rows.append({"bank": bank, "period": period, "indicator": indicator,
                         "tip": "aktiv" if indicator in _ASSET_COMPONENTS else "passiv",
                         "summa": value})
        rows.append({"bank": bank, "period": period, "indicator": "jami_aktivlar",
                     "tip": "aktiv", "summa": total})
    return pd.DataFrame(rows)


def test_discontinuity_detects_broad_level_shift():
    """Every line moves together -> a level shift, not window dressing."""
    report = pd.concat([
        build_report("A", [100, 101, 102, 103, 150, 151]),
        build_report("B", [100, 101, 102, 103, 104, 105]),
    ])
    disc = dict(zip(*det.detect_discontinuity(report)[["bank", "flagged"]].values.T))
    window = dict(zip(*det.detect_window_dressing(report)[["bank", "flagged"]].values.T))
    assert disc["A"] and not disc["B"]
    assert not window["A"]


def test_window_dressing_detects_targeted_spike():
    """Only cash and retail deposits move -> targeted inflation, not a level shift."""
    report = pd.concat([
        build_report("A", [100, 101, 102, 103, 104, 150],
                     spike_lines=("naqd_pullar", "depozitlar_aholi"),
                     spike_period="2026-03", spike_factor=4.0),
        build_report("B", [100, 101, 102, 103, 104, 105]),
    ])
    disc = dict(zip(*det.detect_discontinuity(report)[["bank", "flagged"]].values.T))
    window = dict(zip(*det.detect_window_dressing(report)[["bank", "flagged"]].values.T))
    assert window["A"] and not window["B"]
    assert not disc["A"]


def test_growth_label_does_not_depend_on_window_length():
    """The same spike keeps its label whether or not later periods are present.

    Regression test for the positional rule this replaced: defining window dressing as
    "a jump into the last period" relabelled a bank when the reporting window was cut
    short (DECISIONS.md §9.2).
    """
    full = pd.concat([
        build_report("A", [100, 101, 102, 150, 151, 152]),
        build_report("B", [100, 101, 102, 103, 104, 105]),
    ])
    truncated = full[full["period"].isin(PERIODS[:4])]

    for report in (full, truncated):
        disc = dict(zip(*det.detect_discontinuity(report)[["bank", "flagged"]].values.T))
        window = dict(zip(*det.detect_window_dressing(report)[["bank", "flagged"]].values.T))
        assert disc["A"], "level shift must stay a discontinuity in both windows"
        assert not window["A"]


def test_arithmetic_skips_period_with_unmapped_component():
    """A component ingestion could not map must not read as a fabricated total.

    Dropping a line shrinks the component sum by its whole value, which is
    indistinguishable from a mis-stated total -- and accusing a clean bank costs points,
    so an incomplete period yields no verdict (DECISIONS.md §9.1).
    """
    clean = build_report("A", [100, 101, 102, 103, 104, 105])
    # totals foot exactly: six components of total/6 each
    assert not det.detect_arithmetic(clean)["flagged"].any()

    lost = clean[~((clean["indicator"] == "qimmatli_qogozlar") & (clean["period"] == "2026-01"))]
    assert not det.detect_arithmetic(lost)["flagged"].any()


def test_arithmetic_still_flags_a_complete_but_wrong_total():
    """The guard must not silence a real mismatch when every component is present."""
    report = build_report("A", [100, 101, 102, 103, 104, 105])
    wrong = report.copy()
    mask = (wrong["indicator"] == "jami_aktivlar") & (wrong["period"] == "2026-01")
    wrong.loc[mask, "summa"] = wrong.loc[mask, "summa"] * 1.2
    assert det.detect_arithmetic(wrong)["flagged"].any()


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
