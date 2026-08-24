"""CLI: run the full audit and write the result files. Used by `make audit`.

Drives the same `AuditService` as the API, so the numbers it prints and the files it writes
are the ones the dashboard would show.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import Settings  # noqa: E402
from app.service import AuditService  # noqa: E402

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def build_settings(data: str | None, out: str | None) -> Settings:
    """Environment settings with the two CLI flags applied on top."""
    defaults = Settings.from_env()
    data_dir = Path(data) if data else defaults.data_dir
    overrides = {"result_path": Path(out)} if out else {}
    return Settings(data_dir=data_dir, db_path=defaults.db_path, **overrides)


def main() -> int:
    parser = argparse.ArgumentParser(description="RegTech statistical audit")
    parser.add_argument("--data", default=None, help="dataset directory (default: repo root)")
    parser.add_argument("--out", default=None, help="output CSV path (russian spec variant)")
    args = parser.parse_args()

    settings = build_settings(args.data, args.out)
    service = AuditService(settings)
    ranked = service.run_ranked(service.load_data())
    service.write_result_csv(ranked)

    for audit in ranked:
        reason = ",".join(audit.reason) or "-"
        print(f"  {audit.bank:15s} suspicious={str(audit.suspicious):5s} reason={reason}")
    print(f"\nSuspicious banks: {sum(a.suspicious for a in ranked)}/{len(ranked)}")
    print(f"Result file: {settings.result_path}")
    print(f"Natija file: {settings.natija_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
