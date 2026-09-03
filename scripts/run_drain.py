# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Run Drain on one 2k dataset and save raw parsed output for scoring.

Usage:
    python scripts/run_drain.py --dataset Apache

Reads settings from configs/drain.ini, logs from dataset/<Name>/,
writes results/raw/drain_<name>.csv + .json (with wall time).
"""
from __future__ import annotations

import argparse
import configparser
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="e.g. Apache, Linux, OpenSSH")
    args = ap.parse_args()

    cfg = configparser.ConfigParser()
    cfg.read(ROOT / "configs" / "drain.ini")
    if args.dataset not in cfg:
        raise SystemExit(f"no [{args.dataset}] section in configs/drain.ini")

    log_file = ROOT / "dataset" / args.dataset / f"{args.dataset}_2k.log"
    if not log_file.exists():
        raise SystemExit(f"log file missing: {log_file} (see README section 3)")

    from logparser.Drain import LogParser  # pip/uv extra: drain

    settings = cfg[args.dataset]
    out_dir = ROOT / "results" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    parser = LogParser(
        str(log_file),
        outdir=str(out_dir),
        depth=int(settings.get("depth", 4)),
        simTh=float(settings.get("sim_th", 0.4)),
        maxChild=int(settings.get("max_children", 100)),
        log_format=settings["log_format"],
    )
    parser.parse(str(log_file))
    elapsed = time.time() - t0

    meta = {
        "parser": "drain",
        "dataset": args.dataset,
        "log_format": settings["log_format"],
        "depth": settings.get("depth"),
        "sim_th": settings.get("sim_th"),
        "max_children": settings.get("max_children"),
        "wall_time_s": round(elapsed, 1),
    }
    meta_path = out_dir / f"drain_{args.dataset.lower()}.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"done in {elapsed:.1f}s -> {out_dir}/ (meta: {meta_path.name})")


if __name__ == "__main__":
    main()
