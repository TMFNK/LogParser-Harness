# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Build the stable Tier A result table from committed Drain goldens."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.paths import ROOT as HROOT  # noqa: E402

OUT = HROOT / "results" / "results.md"
EXPECTED = HROOT / "expected"


def main() -> None:
    rows = []
    for p in sorted(EXPECTED.glob("drain_*_2k.json")):
        rows.append(json.loads(p.read_text()))

    lines = [
        "# Drain reproduction (LogHub-2k)",
        "",
        "Scorer: `harness.metrics` (Apache-2.0 implementation of Jiang et al.,",
        "ISSTA'24 GA / PA / FGA / FTA). Drain settings from `configs/drain.yaml`",
        "(logpai/logparser Drain benchmark). Data: Loghub-2.0 `2k_dataset/`,",
        "commit pinned in `configs/datasets.yaml`.",
        "",
        "These reference rows come from the committed Drain golden files in",
        "`expected/`; wall time remains machine-dependent and is recorded only in",
        "each local `results/raw/*_scores.json`.",
        "",
        "| Dataset | Parser | GA | PA | FGA | FTA |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('dataset')} | {r.get('parser')} | {r.get('GA')} | "
            f"{r.get('PA')} | {r.get('FGA')} | {r.get('FTA')} |"
        )
    if not rows:
        lines.append("| — | no committed Drain goldens | — | — | — | — |")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
