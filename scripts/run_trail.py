# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""Run Trail on one 2k dataset. Sibling plugin, not vendored."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.manifest import (  # noqa: E402
    git_sha,
    python_version,
    sha256_file,
    sha256_text,
    uv_lock_hash,
    write_json,
)
from harness.metrics import score_all  # noqa: E402
from harness.paths import log_path, raw_dir  # noqa: E402

SECOPS_DIR = ROOT.parent / "LogParser-Dataset" / "dataset"


def trail_src() -> Path:
    env = os.environ.get("TRAIL_SRC")
    path = Path(env).expanduser().resolve() if env else ROOT.parent / "LogParser-Trail"
    if not (path / "trailparse").is_dir():
        raise SystemExit(
            f"Trail checkout missing: {path}\n"
            "set TRAIL_SRC or clone LogParser-Trail next to this repo"
        )
    return path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _log_format_regex(log_format: str) -> re.Pattern[str]:
    # Same split as logparser Drain.generate_logformat_regex (header vs Content).
    splitters = re.split(r"(<[^<>]+>)", log_format)
    regex = ""
    for k, part in enumerate(splitters):
        if k % 2 == 0:
            regex += re.sub(" +", "\\\\s+", part)
        else:
            header = part.strip("<>")
            regex += f"(?P<{header}>.*?)"
    return re.compile("^" + regex + "$")


def _message(line: str, fmt_re: re.Pattern[str] | None, split_header) -> str:
    if fmt_re is not None:
        m = fmt_re.search(line)
        if m is not None:
            return split_header(m.group("Content"))
    return split_header(line)


def _score_pair(gt_path: Path, parsed_path: Path) -> dict[str, float]:
    gt = _read_csv(gt_path)
    parsed = _read_csv(parsed_path)
    n = min(len(gt), len(parsed))
    return score_all(
        [r["EventId"] for r in gt[:n]],
        [r["EventId"] for r in parsed[:n]],
        [r["EventTemplate"] for r in gt[:n]],
        [r["EventTemplate"] for r in parsed[:n]],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    args = ap.parse_args()

    src = trail_src()
    sys.path.insert(0, str(src))
    from trailparse.io import split_header, write_structured
    from trailparse.miner import Miner

    cfg = yaml.safe_load((src / "configs" / "miner.yaml").read_text())
    st = float(cfg["st"])
    anchor_tokens = int(cfg["anchor_tokens"])

    drain_cfg = yaml.safe_load((ROOT / "configs" / "drain.yaml").read_text())
    fmt_re = None
    if args.dataset == "SecOps":
        log_file = SECOPS_DIR / "SecOps_2k.log"
    else:
        log_file = log_path(args.dataset)
        settings = drain_cfg.get("datasets", {}).get(args.dataset)
        if settings and settings.get("log_format"):
            fmt_re = _log_format_regex(settings["log_format"])
    if not log_file.exists():
        hint = (
            f"\nrun: uv run python scripts/fetch_assets.py --dataset {args.dataset}"
            if args.dataset != "SecOps"
            else ""
        )
        raise SystemExit(f"missing {log_file}{hint}")

    out_dir = raw_dir()
    structured = out_dir / f"{log_file.name}_structured.csv"
    config_hash = sha256_text(yaml.safe_dump(cfg, sort_keys=True))

    miner = Miner(st=st, anchor_tokens=anchor_tokens)
    fed = []
    t0 = time.time()
    for i, raw in enumerate(log_file.read_text().splitlines(), start=1):
        content = _message(raw, fmt_re, split_header)
        fed.append((i, content, miner.feed(i, content)))
    elapsed = time.time() - t0

    rows = []
    for i, content, cluster in fed:
        rows.append(
            {
                "LineId": i,
                "Content": content,
                "EventId": cluster.cid,
                "EventTemplate": miner.template_of(cluster),
                "ParameterList": repr(miner.params_for(content, cluster)),
            }
        )
    write_structured(rows, structured)

    meta = {
        "parser": "trail",
        "parser_impl": "trailparse.Miner",
        "trail_src": str(src),
        "dataset": args.dataset,
        "st": st,
        "anchor_tokens": anchor_tokens,
        "n_templates": len(miner.clusters),
        "config_hash": config_hash,
        "log_sha256": sha256_file(log_file),
        "parsed_csv": str(structured.relative_to(ROOT)),
        "wall_time_s": round(elapsed, 3),
        "git_sha": git_sha(),
        "python": python_version(),
        "uv_lock_sha256": uv_lock_hash(),
        "metrics_impl": "harness.metrics (Apache-2.0, Jiang et al. ISSTA'24 formulas)",
    }
    write_json(out_dir / f"trail_{args.dataset.lower()}.json", meta)

    if args.dataset == "SecOps":
        tight = SECOPS_DIR / "SecOps_2k.log_structured.csv"
        loose = SECOPS_DIR / "SecOps_2k.log_structured_loose.csv"
        if not tight.exists() or not loose.exists():
            raise SystemExit(f"missing SecOps ground truth under {SECOPS_DIR}")
        tight_scores = {
            k: round(v, 6) for k, v in _score_pair(tight, structured).items()
        }
        loose_scores = {
            k: round(v, 6) for k, v in _score_pair(loose, structured).items()
        }
        payload = {
            "parser": "trail",
            "dataset": "SecOps_2k",
            **tight_scores,
            "n_messages": len(rows),
            "n_parsed_templates": len(miner.clusters),
            "wall_time_s": round(elapsed, 3),
            "grouping": "tight",
            "tight": tight_scores,
            "loose": loose_scores,
            "metrics_impl": "harness.metrics",
        }
        write_json(out_dir / "trail_secops_scores.json", payload)
        print(f"done in {elapsed:.1f}s -> {structured}")
        print(json.dumps(payload, indent=2))
        return

    print(f"done in {elapsed:.1f}s -> {structured}")


if __name__ == "__main__":
    main()
