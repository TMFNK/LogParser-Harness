# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Build results/results.md from per-run score JSON files.

Usage:
    python scripts/make_table.py

Reads results/raw/*_scores.json files of shape:
    {"parser": ..., "dataset": ..., "GA": ..., "PA": ..., "FGA": ..., "FTA": ...,
     "wall_time_s": ...}
Writes the markdown table to results/results.md (stdout too).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
OUT = ROOT / "results" / "results.md"


def main() -> None:
    rows = []
    for p in sorted(RAW.glob("*_scores.json")):
        rows.append(json.loads(p.read_text()))

    lines = [
        "# Tier A results",
        "",
        "Eval: Loghub-2.0 `benchmark/evaluation/` (commit recorded in README).",
        "Backend for EFParser: local llama-server + Qwen3.8-2B-Q6_K.",
        "",
        "| Dataset | Parser | GA | PA | FGA | FTA | Time |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('dataset')} | {r.get('parser')} | {r.get('GA')} | "
            f"{r.get('PA')} | {r.get('FGA')} | {r.get('FTA')} | "
            f"{r.get('wall_time_s')}s |"
        )
    if not rows:
        lines.append("| — | no scored runs yet | — | — | — | — | — |")
    lines.append("")
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
