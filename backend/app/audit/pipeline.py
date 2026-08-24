"""Audit orchestration: run every test over every bank, then rank the banks.

One pass produces one `BankAudit` per bank:

  1. the Benford test runs on the loan register (`benford_test.py`);
  2. every detector in the registry scores the aggregate report and the regulatory ratios;
  3. the names of the tests that fired become `reason`, in registry order;
  4. their scores are summed into `composite`, which orders the ranking.

Advisory detectors (last digit, balance identity) are scored and shown in the dashboard but
never enter `reason` or `composite`, so the deciding verdict set stays the autocheck-verified
one -- see `detectors/base.py`.
"""
from __future__ import annotations

import pandas as pd

from ..detectors import ADVISORY, DETECTORS, AuditContext
from ..domain import BankAudit
from .benford_test import BENFORD_THRESHOLD, benford_by_bank

BENFORD_REASON = "benford"
"""Name the Benford test carries in `reason`; detectors use their own `name`."""


def _detector_tables(ctx: AuditContext) -> dict[str, dict[str, tuple[bool, float]]]:
    """Run every detector once: {detector name: {bank: (flagged, score)}}, registry order."""
    return {
        detector.name: {
            str(row["bank"]): (bool(row["flagged"]), float(row["score"]))
            for _, row in detector.run(ctx).iterrows()
        }
        for detector in DETECTORS
    }


def audit_all(
    register: pd.DataFrame,
    normativ: pd.DataFrame,
    report: pd.DataFrame,
    mad_threshold: float = BENFORD_THRESHOLD,
) -> list[BankAudit]:
    """Run every test over all banks and return one audit result per bank."""
    benford_results = benford_by_bank(register, mad_threshold)
    ctx = AuditContext(register=register, normativ=normativ, report=report)
    detector_tables = _detector_tables(ctx)

    audits: list[BankAudit] = []
    for bank in sorted(benford_results, key=str.lower):
        benford_result = benford_results[bank]
        audit = BankAudit(bank=bank, benford=benford_result)

        for name, table in detector_tables.items():
            flagged, score = table.get(bank, (False, 0.0))
            audit.detector_flags[name] = flagged
            audit.detector_scores[name] = score
            if flagged and name not in ADVISORY:
                audit.reason.append(name)
        if benford_result.flagged:
            audit.reason.append(BENFORD_REASON)

        audit.suspicious = bool(audit.reason)
        audit.composite = sum(
            audit.detector_scores.get(r, benford_result.mad or 0.0) for r in audit.reason
        )
        audits.append(audit)

    return audits


def rank_banks(audits: list[BankAudit]) -> list[BankAudit]:
    """Most suspicious banks on top; ties broken by name."""
    return sorted(audits, key=lambda a: (-a.composite, a.bank.lower()))
