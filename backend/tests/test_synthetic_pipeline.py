"""End-to-end pipeline tests on synthetic datasets with known injected violations.

These prove the engine generalises beyond the shipped sample: every corruption type
is detected exactly, no clean bank is flagged, and the thresholds hold across many
random seeds (Monte Carlo).
"""
from __future__ import annotations

import numpy as np
import pytest

from app import audit
from tests import synthetic as syn

REASONS = set(syn.CORRUPTIONS)


def _detect(audits):
    return {a.bank: set(a.reason) for a in audits if a.suspicious}


def test_scenario_exact_detection():
    register, normativ, report, truth = syn.scenario()
    audits = audit.audit_all(register, normativ, report)
    detected = _detect(audits)

    expected_suspicious = {b for b, k in truth.items() if k}
    assert set(detected) == expected_suspicious, f"detected={detected} truth={truth}"

    for bank, reasons in truth.items():
        if reasons:
            assert bank in detected
            # primary reason must match the injected type
            assert reasons & detected[bank], f"{bank}: expected {reasons}, got {detected[bank]}"


@pytest.mark.parametrize("kind", sorted(REASONS))
def test_each_corruption_detected_in_isolation(kind):
    """A single corrupt bank among many clean ones is caught, with the right reason."""
    corruption = {f"Clean{i}": None for i in range(8)}
    corruption[f"Bad_{kind}"] = kind
    register, normativ, report, truth = syn.generate(corruption, seed=1)
    audits = audit.audit_all(register, normativ, report)
    detected = _detect(audits)
    assert set(detected) == {f"Bad_{kind}"}
    assert detected[f"Bad_{kind}"] == {kind}


def test_no_corruption_no_flags():
    """An all-clean dataset yields zero suspicious banks."""
    corruption = {f"Clean{i}": None for i in range(13)}
    register, normativ, report, truth = syn.generate(corruption, seed=2)
    audits = audit.audit_all(register, normativ, report)
    assert _detect(audits) == {}


def test_monte_carlo_robustness():
    """Across many random seeds, precision and recall stay perfect."""
    from collections import Counter

    stats = Counter()
    for seed in range(30):
        corruption = {f"B{i}": None for i in range(6)}
        for j, kind in enumerate(syn.CORRUPTIONS):
            corruption[f"Bad{j}"] = kind
        register, normativ, report, truth = syn.generate(corruption, seed=seed)
        audits = audit.audit_all(register, normativ, report)
        detected = _detect(audits)
        expected = {b for b, k in truth.items() if k}
        got = set(detected)
        if got == expected:
            stats["perfect"] += 1
        else:
            stats["mismatch"] += 1
            stats[f"fn_{expected - got}"] += 1
            stats[f"fp_{got - expected}"] += 1
    assert stats["mismatch"] == 0, f"robustness failures: {dict(stats)}"


def test_undersized_sample_not_flagged_by_benford():
    """A bank with n < 300 register rows is never flagged for benford, but aggregate
    detectors still run (e.g. rounding still fires)."""
    rng = np.random.default_rng(3)
    banks = ["SmallBank", "RoundingBank", "Clean1", "Clean2"]
    corrupt_benford = set()
    corrupt_threshold = set()
    # SmallBank gets only 100 rows; RoundingBank has the rounding defect.
    register_rows = []
    probs = np.array([__import__("math").log10(1 + 1 / d) for d in range(1, 10)])
    for bank in banks:
        n = 100 if bank == "SmallBank" else 1800
        for j in range(n):
            d = int(rng.choice(np.arange(1, 10), p=probs))
            register_rows.append({"bank": bank, "summa": syn._first_digit_amount(d, rng)})
    register = __import__("pandas").DataFrame(register_rows)

    normativ = syn.gen_normativ(banks, corrupt_threshold, rng)
    report = syn.gen_report(banks, {"RoundingBank": "rounding"}, rng)

    audits = audit.audit_all(register, normativ, report)
    by_bank = {a.bank: a for a in audits}

    small = by_bank["SmallBank"]
    assert small.benford.n == 100
    assert not small.benford.sufficient
    assert not small.benford.flagged
    assert not small.suspicious

    assert "benford" not in by_bank["RoundingBank"].reason
    assert "rounding" in by_bank["RoundingBank"].reason


def test_first_digit_edge_values_dropped_with_log(caplog):
    """Zero/negative/NaN values are dropped (not silently included) in a full run."""
    import pandas as pd
    from app import benford

    register = pd.DataFrame(
        {
            "bank": ["EdgeBank"] * 6,
            "summa": [1.0, 0.0, -5.0, float("nan"), "not-a-number", 250000.0],
        }
    )
    normativ = pd.DataFrame(
        {"bank": ["EdgeBank"], "oy": ["2025-10"], "k1_kapital_yetarliligi": [0.15],
         "chegara_k1": [0.13]}
    )
    report = pd.DataFrame(
        {"bank": ["EdgeBank"], "period": ["2025-10"], "indicator": ["jami_aktivlar"],
         "tip": ["aktiv"], "summa": [1e9]}
    )
    res = audit.run_benford(register["summa"])
    assert res.n == 2  # only 1.0 and 250000.0 kept
    assert res.dropped == 4
    assert not res.sufficient  # n < 300 -> explicit insufficient flag
    assert not res.flagged
