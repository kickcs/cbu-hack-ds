"""Per-format report readers behind a common interface.

Each reader turns one source file into canonical records
(bank, period, indicator, tip, summa). Supporting a new format means adding one
reader and registering its extension in READERS -- nothing else changes.
"""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable

import openpyxl
import pandas as pd

from .indicators import map_indicator

log = logging.getLogger(__name__)

ReportRecord = dict
Reader = Callable[[Path], list[ReportRecord]]


def period_key(period: str) -> str:
    """Normalize a reporting-period label to "YYYY-MM"."""
    period = str(period).strip()
    if not period:
        return ""
    parts = re.split(r"\D+", period)
    return f"{parts[0]}-{int(parts[1]):02d}" if len(parts) >= 2 else period


def _record(bank: str, period: str, name: object, tip: object, summa: object) -> ReportRecord | None:
    canon = map_indicator(str(name))
    if canon is None:
        return None
    return {
        "bank": str(bank),
        "period": period_key(period),
        "indicator": canon,
        "tip": str(tip),
        "summa": float(summa),
    }


def read_csv_report(path: Path) -> list[ReportRecord]:
    df = pd.read_csv(path)
    col_bank = next((c for c in ("bank_nomi", "bank") if c in df.columns), None)
    col_period = next((c for c in ("hisobot_oyi", "oy") if c in df.columns), None)
    col_name = next((c for c in ("korsatkich_nomi", "korsatkich") if c in df.columns), None)
    col_tip = next((c for c in ("turi", "tip") if c in df.columns), None)
    col_sum = next((c for c in ("summa_som", "summa") if c in df.columns), None)
    if not all([col_bank, col_period, col_name, col_sum]):
        log.info("ingest: skipping %s (no report columns)", path.name)
        return []
    records = []
    for _, r in df.iterrows():
        rec = _record(r[col_bank], r[col_period], r[col_name], r[col_tip] if col_tip else "", r[col_sum])
        if rec is not None:
            records.append(rec)
    return records


def read_xml_report(path: Path) -> list[ReportRecord]:
    root = ET.parse(path).getroot()
    records = []
    for h in root.iter("hisobot"):
        bank, period = h.get("bank"), h.get("davr")
        for q in h:
            rec = _record(bank, period, q.get("nom"), q.get("tip", ""), q.text)
            if rec is not None:
                records.append(rec)
    return records


def read_xlsx_report(path: Path) -> list[ReportRecord]:
    records = []
    bank = path.stem.replace("_", " ")
    if bank.lower().endswith("banki"):
        bank = "Xalq Banki"
    wb = openpyxl.load_workbook(path, read_only=True)
    try:
        for ws in wb.worksheets:
            period = ws.title
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                if i == 0:
                    continue
                if row is None or len(row) < 4 or row[1] is None:
                    continue
                rec = _record(bank, period, row[1], row[2], row[3])
                if rec is not None:
                    records.append(rec)
    finally:
        wb.close()
    return records


READERS: dict[str, Reader] = {
    ".csv": read_csv_report,
    ".xml": read_xml_report,
    ".xlsx": read_xlsx_report,
}
