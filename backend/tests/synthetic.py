"""Synthetic dataset generator for pipeline-level testing.

Produces the three inputs consumed by app.audit.audit_all (register, normativ,
report) plus a ground-truth map {bank: set(reasons)}. A bank may be clean or carry
one of six injected corruptions: benford, threshold, rounding, arithmetic,
discontinuity, window_dressing. Used by test_synthetic_pipeline.py to prove the
engine generalises beyond the shipped sample.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

PERIODS = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]
K1_LIMIT = 0.13
K1_BAND = 0.005

CORRUPTIONS = (
    "benford",
    "threshold",
    "rounding",
    "arithmetic",
    "discontinuity",
    "window_dressing",
)

_AKTIV = ["naqd_pullar", "banklararo_joylashtirishlar", "kredit_portfeli",
          "kredit_zaxirasi", "qimmatli_qogozlar", "asosiy_vositalar"]
_PASSIV = ["depozitlar_aholi", "depozitlar_yuridik", "banklararo_qarzlar",
           "chiqarilgan_qimmatli_qogozlar", "kapital"]


def _first_digit_amount(d: int, rng: np.random.Generator) -> int:
    k = int(rng.integers(6, 10))
    return int(d * 10 ** k * rng.uniform(1.0, 1.0 + 1.0 / d))


def _benford_probs() -> np.ndarray:
    return np.array([math.log10(1 + 1 / d) for d in range(1, 10)])


def gen_register(banks: list[str], corrupt_benford: set[str], rng: np.random.Generator) -> pd.DataFrame:
    """Loan register: honest banks follow Benford on the first digit; benford-corrupt
    banks draw the first digit uniformly (clearly deviates, like the sample)."""
    rows = []
    probs = _benford_probs()
    for i, bank in enumerate(banks):
        n = int(rng.integers(1500, 2600))
        for j in range(n):
            if bank in corrupt_benford:
                d = int(rng.integers(1, 10))
            else:
                d = int(rng.choice(np.arange(1, 10), p=probs))
            rows.append(
                {
                    "bank": bank,
                    "kredit_id": f"{bank[:3].upper()}{j:06d}",
                    "oy": PERIODS[int(rng.integers(0, len(PERIODS)))],
                    "mijoz_turi": str(rng.choice(["yuridik", "jismoniy"])),
                    "tarmoq": str(rng.choice(["savdo", "qurilish", "qishloq_xoj"])),
                    "summa": _first_digit_amount(d, rng),
                    "stavka_foiz": round(float(rng.uniform(12, 30)), 2),
                    "muddat_oy": int(rng.integers(6, 84)),
                    "tasnif": str(rng.choice(["standart", "standartdan_past", "shubhali", "umidsiz"])),
                }
            )
    return pd.DataFrame(rows)


def gen_normativ(banks: list[str], corrupt_threshold: set[str], rng: np.random.Generator) -> pd.DataFrame:
    """K1 readings: corrupt banks cluster inside (limit, limit+band]; clean spread out."""
    rows = []
    for bank in banks:
        for oy in PERIODS:
            if bank in corrupt_threshold:
                k1 = round(K1_LIMIT + rng.uniform(0.001, K1_BAND), 4)
            else:
                k1 = round(rng.uniform(K1_LIMIT + 0.02, 0.24), 4)
            rows.append(
                {
                    "bank": bank,
                    "oy": oy,
                    "k1_kapital_yetarliligi": k1,
                    "lcr_likvidlik": round(float(rng.uniform(1.0, 2.0)), 4),
                    "k3_bir_qarzdor": round(float(rng.uniform(0.08, 0.25)), 4),
                    "chegara_k1": K1_LIMIT,
                    "chegara_lcr": 1.0,
                    "chegara_k3": 0.25,
                }
            )
    return pd.DataFrame(rows)


def _base_components(rng: np.random.Generator) -> dict[str, float]:
    return {
        "naqd_pullar": float(rng.uniform(2e8, 2e9)),
        "banklararo_joylashtirishlar": float(rng.uniform(1e9, 2e10)),
        "kredit_portfeli": float(rng.uniform(5e10, 5e11)),
        "kredit_zaxirasi": -float(rng.uniform(1e9, 2e10)),
        "qimmatli_qogozlar": float(rng.uniform(1e8, 2e9)),
        "asosiy_vositalar": float(rng.uniform(1e8, 5e9)),
        "depozitlar_aholi": float(rng.uniform(2e10, 2e11)),
        "depozitlar_yuridik": float(rng.uniform(1e10, 1e11)),
        "banklararo_qarzlar": float(rng.uniform(1e9, 2e10)),
        "chiqarilgan_qimmatli_qogozlar": float(rng.uniform(1e9, 2e10)),
    }


def gen_report(banks: list[str], corruption: dict[str, str], rng: np.random.Generator) -> pd.DataFrame:
    """Canonical aggregate report with internally consistent totals for clean banks and
    a single injected defect per corrupt bank."""
    records = []
    for bank in banks:
        base = _base_components(rng)
        growth = [1.0 + rng.uniform(0.01, 0.04) for _ in PERIODS]
        # discontinuity: extra jump into a mid period; window_dressing: into the last.
        kind = corruption.get(bank)
        if kind == "discontinuity":
            growth[-2] *= 1.25
        elif kind == "window_dressing":
            growth[-1] *= 1.25

        scale = 1.0
        for idx, oy in enumerate(PERIODS):
            scale *= growth[idx]
            aktiv = {k: v * scale for k, v in base.items() if k in _AKTIV}
            passiv = {k: v * scale for k, v in base.items() if k in _PASSIV}

            if kind == "rounding":
                aktiv = {k: round(v, -6) for k, v in aktiv.items()}
                passiv = {k: round(v, -6) for k, v in passiv.items()}

            jami_aktiv = sum(aktiv.values())
            # equity (kapital) is the balancing item -> assets == liabilities+capital
            kapital = jami_aktiv - sum(v for k, v in passiv.items() if k != "kapital")
            passiv["kapital"] = kapital
            jami_passiv = sum(passiv.values())

            if kind == "arithmetic" and idx >= len(PERIODS) - 3:
                jami_aktiv = jami_aktiv * 1.02  # inflated total, components untouched

            for k, v in aktiv.items():
                records.append({"bank": bank, "period": oy, "indicator": k, "tip": "aktiv", "summa": v})
            for k, v in passiv.items():
                records.append({"bank": bank, "period": oy, "indicator": k, "tip": "passiv", "summa": v})
            records.append({"bank": bank, "period": oy, "indicator": "jami_aktivlar", "tip": "aktiv", "summa": jami_aktiv})
            records.append({"bank": bank, "period": oy, "indicator": "jami_passivlar", "tip": "passiv", "summa": jami_passiv})
    return pd.DataFrame(records)


def generate(corruption: dict[str, str], seed: int = 0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, set[str]]]:
    """Build the three inputs and the ground truth. corruption maps bank -> type
    (or None for clean)."""
    rng = np.random.default_rng(seed)
    banks = list(corruption.keys())
    corrupt_benford = {b for b, k in corruption.items() if k == "benford"}
    corrupt_threshold = {b for b, k in corruption.items() if k == "threshold"}

    register = gen_register(banks, corrupt_benford, rng)
    normativ = gen_normativ(banks, corrupt_threshold, rng)
    report = gen_report(banks, corruption, rng)

    truth = {b: {k} for b, k in corruption.items() if k}
    return register, normativ, report, truth


def scenario() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, set[str]]]:
    """One balanced scenario: 6 clean banks + one of each corruption."""
    corruption = {
        "Bank_01": None, "Bank_02": None, "Bank_03": None,
        "Bank_04": None, "Bank_05": None, "Bank_06": None,
        "BenfordBank": "benford", "ThresholdBank": "threshold",
        "RoundingBank": "rounding", "ArithmeticBank": "arithmetic",
        "DiscontinuityBank": "discontinuity", "WindowBank": "window_dressing",
    }
    return generate(corruption, seed=0)
