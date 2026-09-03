# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Build results/results.md from per-run score JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.paths import ROOT as HROOT  # noqa: E402
from harness.paths import raw_dir  # noqa: E402

OUT = HROOT / "results" / "results.md"


def main() -> None:
    rows = []
    for p in sorted(raw_dir().glob("*_scores.json")):
        rows.append(json.loads(p.read_text()))

    lines = [
        "# Drain reproduction (LogHub-2k)",
        "",
        "Scorer: `harness.metrics` (Apache-2.0 implementation of Jiang et al.,",
        "ISSTA'24 GA / PA / FGA / FTA). Drain settings from `configs/drain.yaml`",
        "(logpai/logparser Drain benchmark). Data: Loghub-2.0 `2k_dataset/`,",
        "commit pinned in `configs/datasets.yaml`.",
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
    lines.append("Each `results/raw/*_scores.json` carries file hashes and git SHA.")
    lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
