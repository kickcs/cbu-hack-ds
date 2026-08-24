"""Production-like "day-2" dataset generator.

The day-2 autocheck runs the audit against a closed dataset in the same shape as the
sample but with other bank names, other values and possibly renamed report columns and
indicator labels. This module reproduces that: a fresh bank universe, the register and
normativ written from the synthetic generator, and the aggregate reports split across
the three formats (csv / xlsx / xml) with raw, non-canonical indicator labels -- the
exact path `ingest` has to resolve on day 2.

`build()` writes the files and returns the injected ground truth
{bank: set(reasons)} so a caller can compute precision/recall.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from tests import synthetic as syn

# Fresh bank universe, mirroring the sample's spread across report formats:
# 5 csv + 4 xlsx + 4 xml banks, 6 of them carrying one violation each.
BANKS = {
    # clean
    "Zamin Bank": "csv",
    "Nur Bank": "xlsx",
    "Sarbon Bank": "xml",
    "Yulduz Bank": "csv",
    "Kamol Bank": "xlsx",
    "Taraqqiyot Bank": "xml",
    "Baraka Bank": "csv",
    # one corruption per type
    "Oqsoy Bank": "xml",       # benford
    "Yangi Bank": "csv",       # threshold
    "Rivoj Bank": "xlsx",      # rounding
    "Mustaqil Bank": "xml",    # arithmetic
    "Istiqbol Bank": "csv",    # discontinuity
    "Orzu Bank": "xlsx",       # window_dressing
}

VIOLATIONS = {
    "Oqsoy Bank": "benford",
    "Yangi Bank": "threshold",
    "Rivoj Bank": "rounding",
    "Mustaqil Bank": "arithmetic",
    "Istiqbol Bank": "discontinuity",
    "Orzu Bank": "window_dressing",
}

# Raw indicator labels per format. csv uses the human-readable titles from the sample,
# xml the snake_case names, xlsx the upper-case audit sheet titles. A couple of keys
# rotate through two variants by period, like the sample does, so the synonym dict is
# exercised instead of a single identity mapping. All labels map to the canonical keys.
_CSV_NAMES: dict[str, list[str]] = {
    "naqd_pullar": ["Naqd pullar va MB hisobvaraqlari", "Naqd pul va MB dagi mablag'lar"],
    "banklararo_joylashtirishlar": ["Banklararo joylashtirishlar"],
    "kredit_portfeli": ["Kredit portfeli (brutto)", "Berilgan kreditlar (brutto)"],
    "kredit_zaxirasi": ["Kredit zaxirasi"],
    "qimmatli_qogozlar": ["Qimmatli qog'ozlar"],
    "asosiy_vositalar": ["Asosiy vositalar"],
    "jami_aktivlar": ["Jami aktivlar"],
    "depozitlar_aholi": ["Jismoniy shaxslar omonatlari", "Aholi depozitlari"],
    "depozitlar_yuridik": ["Yuridik shaxs depozitlari"],
    "banklararo_qarzlar": ["Banklararo qarzlar"],
    "chiqarilgan_qimmatli_qogozlar": ["Chiqarilgan qimmatli qog'ozlar"],
    "kapital": ["Xususiy kapital", "Ustav kapitali va zaxiralar"],
    "jami_passivlar": ["Jami passivlar va kapital"],
}

_XML_NAMES: dict[str, str] = {
    "naqd_pullar": "naqd_pul_va_mb_dagi_mablag'lar",
    "banklararo_joylashtirishlar": "banklararo_joylashtirishlar",
    "kredit_portfeli": "kredit_portfeli_(brutto)",
    "kredit_zaxirasi": "kredit_zaxirasi",
    "qimmatli_qogozlar": "qimmatli_qog'ozlar",
    "asosiy_vositalar": "asosiy_vositalar",
    "jami_aktivlar": "jami_aktivlar",
    "depozitlar_aholi": "aholi_depozitlari",
    "depozitlar_yuridik": "yuridik_shaxs_depozitlari",
    "banklararo_qarzlar": "banklararo_qarzlar",
    "chiqarilgan_qimmatli_qogozlar": "chiqarilgan_qimmatli_qog'ozlar",
    "kapital": "kapital",
    "jami_passivlar": "jami_passivlar_va_kapital",
}

_XLSX_NAMES: dict[str, str] = {
    "naqd_pullar": "KASSA VA MARKAZIY BANKDAGI MABLAG`",
    "banklararo_joylashtirishlar": "BANKLARARO JOYLASHTIRISHLAR",
    "kredit_portfeli": "KREDIT PORTFELI (BRUTTO)",
    "kredit_zaxirasi": "KREDIT ZAXIRASI",
    "qimmatli_qogozlar": "QIMMATLI QOG`OZLAR",
    "asosiy_vositalar": "ASOSIY VOSITALAR",
    "jami_aktivlar": "JAMI AKTIVLAR",
    "depozitlar_aholi": "AHOLI DEPOZITLARI",
    "depozitlar_yuridik": "YURIDIK SHAXS DEPOZITLARI",
    "banklararo_qarzlar": "BANKLARARO QARZLAR",
    "chiqarilgan_qimmatli_qogozlar": "CHIQARILGAN QIMMATLI QOG`OZLAR",
    "kapital": "KAPITAL",
    "jami_passivlar": "JAMI PASSIVLAR VA KAPITAL",
}


def _csv_label(canonical: str, period_idx: int) -> str:
    variants = _CSV_NAMES[canonical]
    return variants[period_idx % len(variants)]


def _corruption_map() -> dict[str, str | None]:
    return {bank: VIOLATIONS.get(bank) for bank in BANKS}


def _report_rows(report: pd.DataFrame, bank: str) -> pd.DataFrame:
    g = report[report["bank"] == bank]
    periods = sorted(g["period"].unique())
    return g, periods


def _write_csv_report(report: pd.DataFrame, root: Path) -> None:
    banks = [b for b, fmt in BANKS.items() if fmt == "csv"]
    rows = []
    for bank in banks:
        g, periods = _report_rows(report, bank)
        for pidx, period in enumerate(periods):
            for _, r in g[g["period"] == period].iterrows():
                rows.append(
                    {
                        "bank_nomi": bank,
                        "hisobot_oyi": period,
                        "korsatkich_nomi": _csv_label(r["indicator"], pidx),
                        "turi": r["tip"],
                        "summa_som": int(r["summa"]),
                    }
                )
    out = root / "csv"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "hisobotlar.csv", index=False)


def _write_xml_report(report: pd.DataFrame, root: Path) -> None:
    banks = [b for b, fmt in BANKS.items() if fmt == "xml"]
    root_el = ET.Element("hisobotlar")
    for bank in banks:
        g, periods = _report_rows(report, bank)
        for period in periods:
            h = ET.SubElement(root_el, "hisobot", bank=bank, davr=period)
            for _, r in g[g["period"] == period].iterrows():
                q = ET.SubElement(h, "qator", nom=_XML_NAMES[r["indicator"]], tip=r["tip"])
                q.text = str(int(r["summa"]))
    out = root / "xml"
    out.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root_el).write(out / "hisobotlar.xml", encoding="utf-8", xml_declaration=True)


def _write_xlsx_report(report: pd.DataFrame, root: Path) -> None:
    import openpyxl

    banks = [b for b, fmt in BANKS.items() if fmt == "xlsx"]
    out = root / "xlsx"
    out.mkdir(parents=True, exist_ok=True)
    for bank in banks:
        g, periods = _report_rows(report, bank)
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        for period in periods:
            ws = wb.create_sheet(period.replace("-", "_"))
            ws.append(("KOD", "KO`RSATKICH", "TUR", "QIYMAT (so`m)"))
            for i, (_, r) in enumerate(g[g["period"] == period].iterrows()):
                ws.append((f"A{i + 1}", _XLSX_NAMES[r["indicator"]], r["tip"], int(r["summa"])))
        wb.save(out / f"{bank.replace(' ', '_')}.xlsx")


def build(root: str | Path, seed: int = 0) -> dict[str, set[str]]:
    """Write a production-like dataset under `root`; return the ground truth.

    Returns {bank: set(reasons)} for every injected violation -- the value a caller
    compares precision/recall against.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    register, normativ, report, truth = syn.generate(_corruption_map(), seed=seed)

    register.to_csv(root / "kredit_reyestri.csv", index=False)
    normativ.to_csv(root / "normativlar.csv", index=False)
    pd.DataFrame(
        [{"bank": b, "format": fmt, "toifa": "katta" if i < 3 else "o'rta"}
         for i, (b, fmt) in enumerate(BANKS.items())]
    ).to_csv(root / "banklar.csv", index=False)

    _write_csv_report(report, root)
    _write_xml_report(report, root)
    _write_xlsx_report(report, root)

    return {b: {k} for b, k in VIOLATIONS.items()}
