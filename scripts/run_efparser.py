# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Run EFParser on one 2k dataset against the local llama-server backend.

Usage:
    python scripts/run_efparser.py --dataset Apache

Prerequisites:
    ./scripts/start_parser_server.sh start   # answers on 127.0.0.1:8090

Reads configs/efparser.yaml (endpoint + model + EFParser checkout path),
writes results/raw/efparser_<name>.json (with wall time).

NOTE: this is a thin driver. It imports EFParser from the local checkout
and calls its parse entry point with the log file. Adapt the marked lines
to the exact EFParser.py API on first run and record the change here.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="e.g. Apache, Linux, OpenSSH")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "configs" / "efparser.yaml").read_text())

    efparser_src = Path(os.environ.get("EF_PARSER_SRC", cfg["efparser_src"]))
    if not efparser_src.is_absolute():
        efparser_src = ROOT / efparser_src
    if not efparser_src.exists():
        raise SystemExit(
            f"EFParser checkout missing: {efparser_src}\n"
            "clone it yourself (upstream has no license, we never vendor it):\n"
            "  git clone https://github.com/LogAnalysisTech/EFParser-Log-Parser "
            "third_party/EFParser-Log-Parser"
        )
    sys.path.insert(0, str(efparser_src / "EFParser"))

    log_file = ROOT / "dataset" / args.dataset / f"{args.dataset}_2k.log"
    if not log_file.exists():
        raise SystemExit(
            f"log file missing: {log_file}\n"
            f"run: uv run python scripts/fetch_assets.py --dataset {args.dataset}"
        )

    # Health-check the local backend before spending time on parsing.
    base_url = cfg["model"]["base_url"].rstrip("/")
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=10) as r:
            if r.status != 200:
                raise SystemExit(f"model backend returned {r.status}, want 200")
    except SystemExit:
        raise
    except Exception as e:
        raise SystemExit(
            f"model backend not answering at {base_url}/models: {e}\n"
            "run ./scripts/start_parser_server.sh start first"
        ) from e

    # --- ADAPT ON FIRST RUN: call EFParser's entry point here. ---
    # Example shape (verify against EFParser/EFParser.py in the checkout):
    #   from EFParser import EFParser
    #   parser = EFParser(config=cfg["model"], ...)
    #   templates = parser.parse(str(log_file))
    raise SystemExit(
        "driver not wired yet: open scripts/run_efparser.py, verify the "
        "EFParser.py entry point in the local checkout, and replace this "
        "stub with the real call."
    )


if __name__ == "__main__":
    main()
