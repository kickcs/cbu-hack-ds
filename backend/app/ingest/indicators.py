"""Indicator-name mapping: raw column labels -> canonical indicator keys.

Column-name synonyms are mapped via a curated dictionary (all observed variants in the
sample) with a difflib (trigram-like) fallback for unseen names -- this keeps the
ingestion working on the day-2 closed dataset.
"""
from __future__ import annotations

import difflib
import logging
import re

log = logging.getLogger(__name__)

CANONICAL_INDICATORS: tuple[str, ...] = (
    "naqd_pullar",
    "banklararo_joylashtirishlar",
    "kredit_portfeli",
    "kredit_zaxirasi",
    "qimmatli_qogozlar",
    "asosiy_vositalar",
    "jami_aktivlar",
    "depozitlar_aholi",
    "depozitlar_yuridik",
    "banklararo_qarzlar",
    "chiqarilgan_qimmatli_qogozlar",
    "kapital",
    "jami_passivlar",
)

# Every name variant observed across csv/xlsx/xml in the sample -> canonical key.
# Keys are normalized: lowercase, apostrophes/parentheses stripped, spaces collapsed.
_SYNONYMS: dict[str, str] = {
    "naqd pullar va mb hisobvaraqlari": "naqd_pullar",
    "naqd pul va mb dagi mablaglar": "naqd_pullar",
    "naqd pullar va mb dagi mablaglar": "naqd_pullar",
    "kassa va markaziy bankdagi mablag": "naqd_pullar",
    "kassa va markaziy bankdagi mablaglar": "naqd_pullar",
    "kassa va markaziy bankdagi mablaglar va boshqalar": "naqd_pullar",
    "banklararo joylashtirishlar": "banklararo_joylashtirishlar",
    "kredit portfeli": "kredit_portfeli",
    "kredit portfeli brutto": "kredit_portfeli",
    "berilgan kreditlar brutto": "kredit_portfeli",
    "kredit zaxirasi": "kredit_zaxirasi",
    "qimmatli qogozlar": "qimmatli_qogozlar",
    "asosiy vositalar": "asosiy_vositalar",
    "jami aktivlar": "jami_aktivlar",
    "aholi depozitlari": "depozitlar_aholi",
    "jismoniy shaxs depozitlari": "depozitlar_aholi",
    "jismoniy shaxslar omonatlari": "depozitlar_aholi",
    "yuridik shaxs depozitlari": "depozitlar_yuridik",
    "banklararo qarzlar": "banklararo_qarzlar",
    "chiqarilgan qimmatli qogozlar": "chiqarilgan_qimmatli_qogozlar",
    "kapital": "kapital",
    "xususiy kapital": "kapital",
    "ustav kapitali va zaxiralar": "kapital",
    "jami passivlar va kapital": "jami_passivlar",
}

_JUNK = re.compile(r"[^a-z0-9 ]+")
_WS = re.compile(r"\s+")
_FUZZY_MIN_RATIO = 0.7
_UNSEEN: set[str] = set()


def _normalize(name: str) -> str:
    return _WS.sub(" ", _JUNK.sub(" ", name.lower())).strip()


# Canonical keys are valid names too (identity mapping) -- keeps ingestion robust if
# a file already contains canonical labels.
_IDENTITY: dict[str, str] = {_normalize(c): c for c in CANONICAL_INDICATORS}


def map_indicator(name: str) -> str | None:
    """Map a raw indicator name to a canonical key, or None if unmatchable."""
    norm = _normalize(str(name))
    if not norm:
        return None
    if norm in _SYNONYMS:
        return _SYNONYMS[norm]
    if norm in _IDENTITY:
        return _IDENTITY[norm]
    # Fuzzy fallback: best canonical alias match via difflib ratio (trigram-like).
    best, best_ratio = None, 0.0
    for alias, canon in _SYNONYMS.items():
        ratio = difflib.SequenceMatcher(None, norm, alias).ratio()
        if ratio > best_ratio:
            best, best_ratio = canon, ratio
    if best_ratio >= _FUZZY_MIN_RATIO:
        return best
    _UNSEEN.add(norm)
    log.warning("ingest: unmapped indicator %r (best=%r ratio=%.2f)", name, best, best_ratio)
    return None


def unknown_indicator_count() -> int:
    return len(_UNSEEN)
