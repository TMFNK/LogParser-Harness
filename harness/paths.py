# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dataset_dir(name: str) -> Path:
    return ROOT / "dataset" / name


def log_path(name: str) -> Path:
    return dataset_dir(name) / f"{name}_2k.log"


def groundtruth_path(name: str) -> Path:
    return dataset_dir(name) / f"{name}_2k.log_structured.csv"


def raw_dir() -> Path:
    path = ROOT / "results" / "raw"
    path.mkdir(parents=True, exist_ok=True)
    return path
