"""Pytest bootstrap: make backend importable and point relative data paths at the
repo root (where the dataset lives)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND.parent  # repo root

sys.path.insert(0, str(BACKEND))
os.chdir(DATA_DIR)
os.environ.setdefault("DATA_DIR", str(DATA_DIR))
