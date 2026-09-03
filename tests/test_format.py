# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Score JSON schema when a run exists (skipped on a clean checkout)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_score_json_schema_if_present():
    raw = ROOT / "results" / "raw"
    if not raw.exists():
        return
    scores = list(raw.glob("*_scores.json"))
    for path in scores:
        d = json.loads(path.read_text())
        assert {"parser", "dataset", "GA", "PA", "FGA", "FTA"} <= set(d)
