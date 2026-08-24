"""Detector contract shared by every aggregate-report detector.

A detector owns both sides of one violation type:
- `run(ctx)`    -- scores/flags for every bank (DataFrame: bank, score, flagged);
- `evidence(ctx, bank)` -- the concrete rows, periods and figures an auditor would
  eyeball for that bank, as a block dict:
  {"test": ..., "title": ..., "summary": ..., "rows": [{... , "suspect": bool}]}.

Keeping both in one class means the trigger logic exists in exactly one place.
Adding a new detector = one module implementing Detector + one line in registry.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

import pandas as pd

EvidenceBlock = dict


def empty_evidence() -> EvidenceBlock:
    return {"test": "", "title": "", "summary": "", "rows": []}


@dataclass(frozen=True)
class AuditContext:
    """Every dataset the audit works with; detectors pick what they need."""

    register: pd.DataFrame | None = None
    normativ: pd.DataFrame | None = None
    report: pd.DataFrame | None = None


class Detector(ABC):
    name: ClassVar[str]
    # Advisory detectors run and are shown in the dashboard, but never contribute
    # to `reason`/`composite` -- the deciding verdict set stays autocheck-verified.
    advisory: ClassVar[bool] = False

    @abstractmethod
    def run(self, ctx: AuditContext) -> pd.DataFrame:
        """Score all banks -> DataFrame with columns (bank, score, flagged)."""

    @abstractmethod
    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        """Evidence block for one bank (assumes the detector fired for it)."""


def bank_report(report: pd.DataFrame, bank: str) -> pd.DataFrame:
    return report[report["bank"] == bank]
