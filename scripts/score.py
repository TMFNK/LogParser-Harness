# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Score a parsed structured CSV against LogHub-2k ground truth."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.manifest import (  # noqa: E402
    git_sha,
    sha256_file,
    uv_lock_hash,
    write_json,
)
from harness.metrics import score_rows  # noqa: E402
from harness.paths import groundtruth_path, raw_dir  # noqa: E402


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--parser", default="drain")
    ap.add_argument(
        "--parsed",
        help="structured CSV; default results/raw/<log>_structured.csv",
    )
    args = ap.parse_args()

    gt_path = groundtruth_path(args.dataset)
    if not gt_path.exists():
        raise SystemExit(
            f"missing {gt_path}\n"
            f"run: uv run python scripts/fetch_assets.py --dataset {args.dataset}"
        )
    parsed_path = (
        Path(args.parsed)
        if args.parsed
        else raw_dir() / f"{args.dataset}_2k.log_structured.csv"
    )
    if not parsed_path.exists():
        raise SystemExit(f"missing parsed output {parsed_path}")

    gt = _read_csv(gt_path)
    parsed = _read_csv(parsed_path)
    try:
        scores = score_rows(gt, parsed)
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"cannot score {parsed_path}: {exc}") from exc
    run_meta_path = raw_dir() / f"{args.parser}_{args.dataset.lower()}.json"
    wall = None
    if run_meta_path.exists():
        wall = json.loads(run_meta_path.read_text()).get("wall_time_s")

    payload = {
        "parser": args.parser,
        "dataset": f"{args.dataset}_2k",
        **{k: round(v, 6) for k, v in scores.items()},
        "n_messages": len(gt),
        "wall_time_s": wall,
        "groundtruth_sha256": sha256_file(gt_path),
        "parsed_sha256": sha256_file(parsed_path),
        "git_sha": git_sha(),
        "uv_lock_sha256": uv_lock_hash(),
        "metrics_impl": "harness.metrics",
        "metrics_paper": "Jiang et al., ISSTA 2024, arXiv:2308.10828 §4.2",
    }
    out = raw_dir() / f"{args.parser}_{args.dataset.lower()}_scores.json"
    write_json(out, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
