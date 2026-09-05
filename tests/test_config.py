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
        assert len(cfg["datasets"][name]["log"]["sha256"]) == 64
        assert len(cfg["datasets"][name]["structured"]["sha256"]) == 64


def test_expected_drain_golden_keys():
    import json

    for name in ("apache", "linux", "openssh"):
        path = ROOT / "expected" / f"drain_{name}_2k.json"
        data = json.loads(path.read_text())
        assert data["parser"] == "drain"
        assert set(data) >= {"GA", "PA", "FGA", "FTA", "parser", "dataset"}


def test_spell_yaml_pins_tau():
    cfg = yaml.safe_load((ROOT / "configs" / "spell.yaml").read_text())
    for name in ("Apache", "Linux", "OpenSSH"):
        assert cfg["datasets"][name]["tau"] == 0.5
        assert "<Content>" in cfg["datasets"][name]["log_format"]


def test_expected_spell_golden_keys():
    import json

    for name in ("apache", "linux", "openssh"):
        path = ROOT / "expected" / f"spell_{name}_2k.json"
        data = json.loads(path.read_text())
        assert data["parser"] == "spell"
        assert data["n_messages"] == 2000
        assert set(data) >= {"GA", "PA", "FGA", "FTA", "parser", "dataset"}


def test_trail_golden_keys():
    import json

    for name in ("apache", "linux", "openssh", "secops"):
        path = ROOT / "expected" / f"trail_{name}_2k.json"
        data = json.loads(path.read_text())
        assert data["parser"] == "trail"
        assert set(data) >= {
            "GA",
            "PA",
            "FGA",
            "FTA",
            "parser",
            "dataset",
            "n_messages",
        }
