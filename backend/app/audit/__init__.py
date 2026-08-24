"""The audit itself: what is tested, in which order, and what comes out of it.

  sampling (app/sampling.py)  the MIN_SAMPLE guard every register-based test obeys
  benford_test.py             the Benford test for one bank's loan amounts
  pipeline.py                 all tests over all banks, then the ranking
  results.py                  the format of the result file
  evidence.py                 the figures behind a verdict, for the dashboard

Everything a caller needs is re-exported here: `from app import audit`.
"""
from __future__ import annotations

from ..domain import BankAudit, BenfordResult
from ..sampling import MIN_SAMPLE, is_sample_sufficient
from .benford_test import BENFORD_THRESHOLD, benford_by_bank, run_benford
from .evidence import benford_evidence, collect_evidence
from .pipeline import BENFORD_REASON, audit_all, rank_banks
from .results import NATIJA_COLUMNS, RESULT_COLUMNS, to_suspicious_frame

__all__ = [
    "BENFORD_REASON",
    "BENFORD_THRESHOLD",
    "MIN_SAMPLE",
    "NATIJA_COLUMNS",
    "RESULT_COLUMNS",
    "BankAudit",
    "BenfordResult",
    "audit_all",
    "benford_by_bank",
    "benford_evidence",
    "collect_evidence",
    "is_sample_sufficient",
    "rank_banks",
    "run_benford",
    "to_suspicious_frame",
]
