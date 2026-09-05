# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Run Spell on one 2k dataset with pinned benchmark settings."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.manifest import (  # noqa: E402
    git_sha,
    python_version,
    sha256_file,
    sha256_text,
    uv_lock_hash,
    write_json,
)
from harness.paths import log_path, raw_dir  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "configs" / "spell.yaml").read_text())
    if args.dataset not in cfg["datasets"]:
        raise SystemExit(f"no dataset {args.dataset} in configs/spell.yaml")
    settings = cfg["datasets"][args.dataset]
    log_file = log_path(args.dataset)
    if not log_file.exists():
        raise SystemExit(
            f"missing {log_file}\n"
            f"run: uv run python scripts/fetch_assets.py --dataset {args.dataset}"
        )

    from logparser.Spell import LogParser

    out_dir = raw_dir()
    indir = str(log_file.parent)
    filename = log_file.name
    config_hash = sha256_text(yaml.safe_dump(settings, sort_keys=True))

    t0 = time.time()
    parser = LogParser(
        log_format=settings["log_format"],
        indir=indir,
        outdir=str(out_dir),
        tau=float(settings["tau"]),
        rex=list(settings.get("regex") or []),
    )
    parser.parse(filename)
    elapsed = time.time() - t0

    structured = out_dir / f"{filename}_structured.csv"
    meta = {
        "parser": "spell",
        "parser_impl": "logparser3 / logpai.Spell",
        "dataset": args.dataset,
        "log_format": settings["log_format"],
        "tau": settings["tau"],
        "regex": settings.get("regex") or [],
        "config_hash": config_hash,
        "log_sha256": sha256_file(log_file),
        "parsed_csv": str(structured.relative_to(ROOT)),
        "wall_time_s": round(elapsed, 3),
        "git_sha": git_sha(),
        "python": python_version(),
        "uv_lock_sha256": uv_lock_hash(),
        "metrics_impl": "harness.metrics (Apache-2.0, Jiang et al. ISSTA'24 formulas)",
    }
    write_json(out_dir / f"spell_{args.dataset.lower()}.json", meta)
    print(f"done in {elapsed:.1f}s -> {structured}")


if __name__ == "__main__":
    main()
