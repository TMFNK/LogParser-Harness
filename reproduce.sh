#!/usr/bin/env bash
# One-command Tier A reproduction: Drain + EFParser on Apache_2k.
# Run from the repo root: ./reproduce.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "=== [1/5] env ==="
uv sync

echo "=== [2/5] Drain on Apache_2k ==="
uv run python scripts/run_drain.py --dataset Apache

echo "=== [3/5] model server (llama.cpp + Qwen3.8-2B-Q6_K) ==="
./scripts/start_parser_server.sh start

echo "=== [4/5] EFParser on Apache_2k ==="
uv run python scripts/run_efparser.py --dataset Apache

echo "=== [5/5] results table ==="
uv run python scripts/make_table.py

./scripts/start_parser_server.sh stop
echo "done -> results/results.md"
