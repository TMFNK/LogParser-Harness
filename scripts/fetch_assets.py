# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Download LogHub-2k files and verify sha256."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.paths import dataset_dir  # noqa: E402

RAW_BASE = "https://raw.githubusercontent.com/logpai/Loghub-2.0"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with urllib.request.urlopen(url) as resp, tmp.open("wb") as out:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(dest)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", action="append", dest="datasets")
    ap.add_argument(
        "--write-checksums",
        action="store_true",
        help="fill sha256 placeholders in configs/datasets.yaml",
    )
    args = ap.parse_args()

    cfg_path = ROOT / "configs" / "datasets.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    commit = cfg["source"]["commit"]
    names = args.datasets or list(cfg["datasets"])

    for name in names:
        if name not in cfg["datasets"]:
            raise SystemExit(f"unknown dataset {name}")
        spec = cfg["datasets"][name]
        out_dir = dataset_dir(name)
        for kind, filename in (
            ("log", f"{name}_2k.log"),
            ("structured", f"{name}_2k.log_structured.csv"),
        ):
            rel = spec[kind]["path"]
            url = f"{RAW_BASE}/{commit}/{rel}"
            dest = out_dir / filename
            print(f"fetch {url} -> {dest}")
            _download(url, dest)
            digest = _sha256(dest)
            expected = spec[kind].get("sha256") or ""
            if expected and expected != "PLACEHOLDER":
                if digest != expected:
                    raise SystemExit(
                        f"sha256 mismatch for {dest}: got {digest}, want {expected}"
                    )
                print(f"  ok {digest}")
            else:
                print(f"  sha256 {digest} (not pinned yet)")
                spec[kind]["sha256"] = digest

    if args.write_checksums:
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
        print(f"updated checksums in {cfg_path}")


if __name__ == "__main__":
    main()
