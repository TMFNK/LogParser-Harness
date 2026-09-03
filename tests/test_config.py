# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_drain_yaml_has_loghub_apache_settings():
    cfg = yaml.safe_load((ROOT / "configs" / "drain.yaml").read_text())
    apache = cfg["datasets"]["Apache"]
    assert apache["st"] == 0.5
    assert apache["depth"] == 4
    assert apache["log_format"] == r"\[<Time>\] \[<Level>\] <Content>"


def test_datasets_yaml_pins_commit():
    cfg = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text())
    assert len(cfg["source"]["commit"]) == 40
    for name in ("Apache", "Linux", "OpenSSH"):
        assert "2k_dataset" in cfg["datasets"][name]["log"]["path"]


def test_expected_golden_keys():
    import json

    path = ROOT / "expected" / "drain_apache_2k.json"
    data = json.loads(path.read_text())
    assert set(data) >= {"GA", "PA", "FGA", "FTA", "parser", "dataset"}
