"""Application settings: every filesystem path the backend touches, in one place.

`DATA_DIR` and `DB_PATH` come from the environment (Docker sets both). The dataset lives in
its own directory (`data/`) so that the scan in `ingest.iter_data_files` sees source files
and nothing else; the result files stay one level above it, at the project root, because the
autocheck reads them there by name. Hence `output_dir` defaults to `data_dir.parent` --
point `DATA_DIR` at a temporary dataset and its results follow it instead of landing in the
repo. A caller may name either result path outright, which is how `cli.py` honours `--out`.

The result is written in BOTH spec variants, because the spec exists in two languages and it
is unknown which one the day-2 autocheck matches:
- русская версия §8:      результат/подозрительные_банки.csv
- официальная (узб.) §5:  natija/shubhali_banklar.csv
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent

DATA_DIR_NAME = "data"
RESULT_DIR_NAME = "результат"
RESULT_FILE_NAME = "подозрительные_банки.csv"
NATIJA_DIR_NAME = "natija"
NATIJA_FILE_NAME = "shubhali_banklar.csv"

# Leading dot: uploads live under the dataset directory but must never be swept up by the
# dataset scan, which skips dot-directories (see ingest.iter_data_files).
UPLOAD_DIR_NAME = ".uploads"


class Settings(BaseSettings):
    """Paths the audit reads from and writes to, resolved from the environment."""

    model_config = SettingsConfigDict(extra="ignore", frozen=True)

    data_dir: Path = Field(
        default=REPO_ROOT / DATA_DIR_NAME,
        description="Dataset directory: loan register, regulatory ratios and report files.",
    )
    output_dir: Path = Field(
        default=REPO_ROOT,
        description="Where the two result directories are written; one level above the dataset.",
    )
    db_path: Path = Field(
        default=BACKEND_ROOT / "data" / "regtech.db",
        description="SQLite file with raw files, canonical report lines and audit runs.",
    )
    upload_dir: Path = Field(
        default=REPO_ROOT / DATA_DIR_NAME / UPLOAD_DIR_NAME,
        description="Uploaded submissions, one directory per queued report.",
    )
    result_path: Path = Field(
        default=REPO_ROOT / RESULT_DIR_NAME / RESULT_FILE_NAME,
        description="Result file, russian spec variant (банк, значение_mad, причина).",
    )
    natija_path: Path = Field(
        default=REPO_ROOT / NATIJA_DIR_NAME / NATIJA_FILE_NAME,
        description="Result file, official uzbek spec variant (bank, mad_qiymati, sabab).",
    )

    @model_validator(mode="before")
    @classmethod
    def _derive_result_paths(cls, values: Any) -> Any:
        """Anchor the uploads to `data_dir` and the results to `output_dir` above it."""
        if not isinstance(values, dict):
            return values
        data_dir = Path(values.get("data_dir") or REPO_ROOT / DATA_DIR_NAME)
        output_dir = Path(values.get("output_dir") or data_dir.parent)
        values.setdefault("output_dir", output_dir)
        values.setdefault("result_path", output_dir / RESULT_DIR_NAME / RESULT_FILE_NAME)
        values.setdefault("natija_path", output_dir / NATIJA_DIR_NAME / NATIJA_FILE_NAME)
        values.setdefault("upload_dir", data_dir / UPLOAD_DIR_NAME)
        return values

    @classmethod
    def from_env(cls) -> "Settings":
        """Read DATA_DIR / DB_PATH from the environment, falling back to repo defaults."""
        return cls()
