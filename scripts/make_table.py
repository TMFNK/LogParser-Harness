# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Build the stable Tier A result table from committed parser goldens."""

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
    for prefix in ("drain", "spell", "trail"):
        for p in sorted(EXPECTED.glob(f"{prefix}_*_2k.json")):
            row = json.loads(p.read_text())
            if row.get("dataset") == "SecOps_2k":
                continue
            rows.append(row)

    lines = [
        "# LogHub-2k reproduction (Drain + Spell + Trail)",
        "",
        "Scorer: `harness.metrics` (Apache-2.0 implementation of Jiang et al.,",
        "ISSTA'24 GA / PA / FGA / FTA). Drain settings from `configs/drain.yaml`",
        "(logpai/logparser Drain benchmark). Spell settings from",
        "`configs/spell.yaml` (same logparser3 dependency, tau=0.5, untuned).",
        "Trail settings from the sibling",
        "`LogParser-Trail` checkout (`configs/miner.yaml`, revision pinned in",
        "each `expected/trail_*_2k.json`). Data: Loghub-2.0 `2k_dataset/`,",
        "commit pinned in `configs/datasets.yaml`.",
        "",
        "These reference rows come from the committed golden files in",
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
        lines.append("| — | no committed goldens | — | — | — | — |")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
