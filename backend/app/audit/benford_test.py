"""The Benford test as the audit sees it: raw amounts in, a per-bank verdict out.

Bridges the pure statistics of `app/benford/` to the domain result, and enforces the rule
that decides the whole task (TZ §5): the test runs on the loan register -- 1400-2600 rows
per bank -- and NOT on the aggregate report, which holds ~78 numbers in total. Below
`MIN_SAMPLE` rows the result carries `sufficient=False` and the bank is never flagged on the
strength of this test.
"""
from __future__ import annotations

import pandas as pd

from .. import benford
from ..domain import BenfordResult
from ..ingest.register import bank_column
from ..sampling import is_sample_sufficient

BENFORD_THRESHOLD = benford.MAD_MARGINAL
"""MAD above which the distribution is nonconforming -- Nigrini (2012) boundary."""


def run_benford(values, threshold: float = BENFORD_THRESHOLD) -> BenfordResult:
    """Run the first-digit MAD and chi-square tests on a raw sequence of amounts."""
    digits, dropped = benford.extract_first_digits(values)
    n = int(digits.size)
    result = BenfordResult(n=n, dropped=dropped, sufficient=is_sample_sufficient(n))
    if n == 0:
        return result

    observed = benford.empirical_distribution(digits)
    result.mad = benford.benford_mad(observed)
    result.mad_label = benford.mad_label(result.mad)
    result.chi2, result.chi2_p = benford.chi_square_test(digits)
    result.threshold = threshold
    if result.sufficient:
        result.calibrated_threshold = benford.bootstrap_mad_threshold(n)
    result.flagged = result.sufficient and result.mad > threshold
    return result


def benford_by_bank(
    register: pd.DataFrame, threshold: float = BENFORD_THRESHOLD
) -> dict[str, BenfordResult]:
    """Run the test separately for every bank present in the loan register."""
    return {
        str(bank): run_benford(g["summa"], threshold=threshold)
        for bank, g in register.groupby(bank_column(register))
    }
