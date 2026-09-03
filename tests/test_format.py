# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Smoke test: parsed-output rows match the eval input format."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_raw_dir_exists():
    assert (ROOT / "results" / "raw").exists()


def test_drain_meta_schema():
    for meta in (ROOT / "results" / "raw").glob("drain_*.json"):
        d = json.loads(meta.read_text())
        assert {"parser", "dataset", "wall_time_s"} <= set(d)
