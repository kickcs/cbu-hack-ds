"""Last-digit uniformity test (TZ §4 bonus): on organic loan amounts the last
digit is close to uniform; rounding or fabrication skews it heavily.

Runs on the loan register (like Benford) and honours the same MIN_SAMPLE guard.
Advisory -- thresholds are documented in DECISIONS.md §4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from ..ingest.register import amount_column, bank_column, loan_amounts
from ..sampling import is_sample_sufficient
from .base import AuditContext, Detector, EvidenceBlock, empty_evidence

LAST_DIGIT_ALPHA = 0.001  # p-value to fire; sample: clean banks chi2 <= 19, corrupted >= 4278

_DIGITS = range(10)
_SUSPECT_SHARE_DEVIATION = 0.05  # |share - 0.1| that marks a digit in evidence


def last_digits(values: pd.Series) -> pd.Series:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    return vals.abs().round().astype("int64").astype(str).str[-1].astype(int)


def uniformity_test(digits: pd.Series) -> tuple[float, float]:
    """Chi-square of observed last-digit counts against the uniform expectation."""
    obs = digits.value_counts().reindex(_DIGITS, fill_value=0).to_numpy()
    chi2, p = stats.chisquare(obs, np.full(10, obs.sum() / 10))
    return float(chi2), float(p)


class LastDigitUniformityDetector(Detector):
    name = "last_digit"
    advisory = True
    requires = ("register",)

    def run(self, ctx: AuditContext) -> pd.DataFrame:
        rows = []
        amounts = amount_column(ctx.register)
        for bank, g in ctx.register.groupby(bank_column(ctx.register)):
            digits = last_digits(g[amounts])
            if not is_sample_sufficient(len(digits)):
                rows.append({"bank": str(bank), "score": 0.0, "flagged": False})
                continue
            _, p = uniformity_test(digits)
            rows.append({"bank": str(bank), "score": float(1.0 - p), "flagged": bool(p < LAST_DIGIT_ALPHA)})
        return pd.DataFrame(rows)

    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        digits = last_digits(loan_amounts(ctx.register, bank))
        if digits.empty:
            return empty_evidence()
        chi2, p = uniformity_test(digits)
        n = len(digits)
        counts = digits.value_counts().reindex(_DIGITS, fill_value=0)
        rows = [
            {
                "digit": int(d),
                "count": int(counts[d]),
                "expected_count": round(n / 10, 1),
                "share": round(float(counts[d]) / n, 4),
                "suspect": abs(float(counts[d]) / n - 0.1) > _SUSPECT_SHARE_DEVIATION,
            }
            for d in _DIGITS
        ]
        return {
            "test": self.name,
            "title": "Last digit is not uniform",
            "title_key": "evidence.blocks.last_digit.title",
            "summary": f"chi2 = {chi2:.1f}, p = {p:.2g} against a uniform last digit "
            f"across {n} loan amounts in the register.",
            "summary_key": "evidence.blocks.last_digit.summary",
            "summary_args": {"chi2": f"{chi2:.1f}", "p": f"{p:.2g}", "n": n},
            "rows": rows,
        }
