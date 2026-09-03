# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Fail if scored Drain metrics drift from the committed golden file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = ("GA", "PA", "FGA", "FTA")
IDENTITY_KEYS = ("parser", "dataset", "n_messages")
PIN_KEYS = (
    "config_hash",
    "log_sha256",
    "groundtruth_sha256",
    "parsed_sha256",
    "dataset_git_sha",
)


def mismatches(
    expected: dict[str, object], actual: dict[str, object], atol: float
) -> list[str]:
    failed = []
    for key in IDENTITY_KEYS:
        if key not in expected or key not in actual:
            failed.append(f"{key}: missing from expected or actual")
        elif expected[key] != actual[key]:
            failed.append(f"{key}: expected {expected[key]!r}, got {actual[key]!r}")
    for key in KEYS:
        if key not in expected or key not in actual:
            failed.append(f"{key}: missing from expected or actual")
        elif abs(float(expected[key]) - float(actual[key])) > atol:
            failed.append(f"{key}: expected {expected[key]}, got {actual[key]}")
    for key in PIN_KEYS:
        if key not in expected:
            continue
        if key not in actual:
            failed.append(f"{key}: missing from actual")
        elif expected[key] != actual[key]:
            failed.append(f"{key}: expected {expected[key]!r}, got {actual[key]!r}")
    return failed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--expected",
        default=str(ROOT / "expected" / "drain_apache_2k.json"),
    )
    ap.add_argument(
        "--actual",
        default=str(ROOT / "results" / "raw" / "drain_apache_scores.json"),
    )
    ap.add_argument("--atol", type=float, default=1e-6)
    args = ap.parse_args()

    expected = json.loads(Path(args.expected).read_text())
    actual_path = Path(args.actual)
    if not actual_path.exists():
        raise SystemExit(f"missing scores {actual_path}")
    actual = json.loads(actual_path.read_text())

    failed = mismatches(expected, actual, args.atol)
    if failed:
        raise SystemExit("golden mismatch:\n  " + "\n  ".join(failed))
    print(f"ok: {actual_path} matches {args.expected}")


if __name__ == "__main__":
    main()
