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
    # Which AuditContext frames `run` dereferences. A submission uploaded through the
    # dashboard may carry only one of the three datasets, and a detector whose input is
    # absent must be skipped and reported as skipped -- not crash, and not score zero,
    # which would read as "tested, nothing found".
    requires: ClassVar[tuple[str, ...]] = ("report",)

    @abstractmethod
    def run(self, ctx: AuditContext) -> pd.DataFrame:
        """Score all banks -> DataFrame with columns (bank, score, flagged)."""

    @abstractmethod
    def evidence(self, ctx: AuditContext, bank: str) -> EvidenceBlock:
        """Evidence block for one bank (assumes the detector fired for it)."""


def bank_report(report: pd.DataFrame, bank: str) -> pd.DataFrame:
    return report[report["bank"] == bank]


def has_dataset(ctx: AuditContext, name: str) -> bool:
    """True when `ctx` carries a usable frame under `name` (present and non-empty)."""
    frame = getattr(ctx, name, None)
    return frame is not None and not frame.empty


def runnable(detectors: tuple[Detector, ...], ctx: AuditContext) -> tuple[Detector, ...]:
    """The detectors whose required datasets are all present in `ctx`."""
    return tuple(d for d in detectors if all(has_dataset(ctx, name) for name in d.requires))
