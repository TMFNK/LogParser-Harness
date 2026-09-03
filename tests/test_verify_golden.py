# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
from scripts.verify_golden import mismatches


def test_golden_checks_run_identity():
    expected = {
        "parser": "drain",
        "dataset": "Apache_2k",
        "n_messages": 2000,
        "GA": 1.0,
        "PA": 1.0,
        "FGA": 1.0,
        "FTA": 1.0,
    }
    actual = {**expected, "dataset": "Linux_2k"}
    assert mismatches(expected, actual, 1e-6) == [
        "dataset: expected 'Apache_2k', got 'Linux_2k'"
    ]


def test_golden_allows_metric_tolerance():
    expected = {
        "parser": "drain",
        "dataset": "Apache_2k",
        "n_messages": 2000,
        "GA": 1.0,
        "PA": 1.0,
        "FGA": 1.0,
        "FTA": 1.0,
    }
    actual = {**expected, "FTA": 0.9999995}
    assert mismatches(expected, actual, 1e-6) == []


def test_golden_checks_declared_input_pins():
    expected = {
        "parser": "trail",
        "dataset": "SecOps_2k",
        "n_messages": 2000,
        "GA": 1.0,
        "PA": 1.0,
        "FGA": 1.0,
        "FTA": 1.0,
        "config_hash": "expected",
    }
    actual = {**expected, "config_hash": "different"}
    assert mismatches(expected, actual, 1e-6) == [
        "config_hash: expected 'expected', got 'different'"
    ]
