"""Day-2 dry run: audit a fresh production-like dataset and report precision/recall.

The day-2 autocheck swaps in a closed dataset of the same shape but different names and
values. This script rehearses that: it generates a new dataset (`tests/day2.py`), loads it
through the exact file-based ingest path the API/CLI use, runs the audit, and compares the
verdicts against the injected ground truth.

Usage:
    python3 scripts/verify_day2.py [--seed N] [--seeds N] [--keep DIR]

Exits non-zero when precision or recall is below 1.0, or when any indicator label is left
unmapped.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import ingest  # noqa: E402
from app.config import Settings  # noqa: E402
from app.service import AuditService  # noqa: E402
from tests import day2  # noqa: E402

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def _score_detection(ranked, truth: dict[str, set[str]]) -> tuple[int, int, int, int]:
    """Compare the audit verdicts against the ground truth.

    Returns (tp, fp, fn, total). A bank the audit flagged but with none of the injected
    reasons counts as a miss on recall, and a clean bank flagged at all is a false
    positive.
    """
    detected = {a.bank: set(a.reason) for a in ranked if a.suspicious}
    expected = {b for b, reasons in truth.items() if reasons}
    tp = len(expected & detected.keys())
    fp = len(set(detected) - expected)
    fn = sum(1 for b in expected if b not in detected or not (truth[b] & detected[b]))
    return tp, fp, fn, len(expected)


def _run(data_dir: Path, seed: int, keep: bool) -> tuple[int, int, int, int, int]:
    """One seed: build the dataset, run the pipeline, score it.

    Returns (tp, fp, fn, total, unknown_labels).
    """
    truth = day2.build(data_dir, seed=seed)
    settings = Settings(data_dir=data_dir, db_path=data_dir / "audit.db", upload_dir=data_dir / ".uploads")
    service = AuditService(settings)
    ranked = service.run_ranked(service.load_data())
    unknown = ingest.unknown_indicator_count()
    if not keep:
        shutil.rmtree(data_dir, ignore_errors=True)
    tp, fp, fn, total = _score_detection(ranked, truth)
    return tp, fp, fn, total, unknown


def main() -> int:
    parser = argparse.ArgumentParser(description="Day-2 dry run of the audit")
    parser.add_argument("--seed", type=int, default=0, help="first seed (or the only one)")
    parser.add_argument("--seeds", type=int, default=1, help="Monte Carlo: number of seeds")
    parser.add_argument("--keep", type=Path, default=None, help="keep the last generated dataset here")
    args = parser.parse_args()

    seeds = range(args.seed, args.seed + args.seeds) if args.seeds > 1 else [args.seed]

    tp = fp = fn = total = 0
    max_unknown = 0
    failures = []
    for seed in seeds:
        keep_dir = args.keep if (args.keep is not None and seed == seeds[-1]) else None
        if keep_dir is None:
            keep_dir = Path(tempfile.mkdtemp(prefix=f"day2_{seed}_"))
        s_tp, s_fp, s_fn, s_total, unknown = _run(keep_dir, seed, keep=keep_dir == args.keep)
        tp += s_tp
        fp += s_fp
        fn += s_fn
        total += s_total
        max_unknown = max(max_unknown, unknown)
        if s_fp or s_fn:
            failures.append((seed, s_tp, s_fp, s_fn))
        print(f"  seed={seed:3d} tp={s_tp} fp={s_fp} fn={s_fn} total={s_total} unknown_labels={unknown}")

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / total if total else 1.0
    print(f"\nPrecision={precision:.3f}  Recall={recall:.3f}  ({tp}tp / {fp}fp / {fn}fn of {total})")
    print(f"Unmapped indicator labels: {max_unknown}")

    ok = precision == 1.0 and recall == 1.0 and max_unknown == 0
    if failures:
        print(f"FAIL: seed(s) with a miss: {failures}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
