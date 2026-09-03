#!/usr/bin/env bash
# Drain-only reproduction (Phase 1). EFParser is not part of this path.
# Usage: ./reproduce.sh --drain-only
#        ./reproduce.sh Apache Linux   # extra 2k datasets after Apache
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "usage: $0 --drain-only [Apache] [Linux] [OpenSSH]"
  echo "Phase 1 ships Drain only. Pass extra dataset names after --drain-only."
  exit 0
fi

if [[ "${1:-}" != "--drain-only" ]]; then
  echo "This release reproduces Drain only." >&2
  echo "Run: ./reproduce.sh --drain-only" >&2
  echo "EFParser is deferred (unlicensed upstream, unwired driver)." >&2
  exit 2
fi
shift
datasets=("$@")
if [[ ${#datasets[@]} -eq 0 ]]; then
  datasets=(Apache)
fi

echo "=== env ==="
uv sync --extra dev

echo "=== fetch ==="
fetch_args=()
for ds in "${datasets[@]}"; do
  fetch_args+=(--dataset "$ds")
done
uv run python scripts/fetch_assets.py "${fetch_args[@]}"

echo "=== drain + score ==="
for ds in "${datasets[@]}"; do
  uv run python scripts/run_drain.py --dataset "$ds"
  uv run python scripts/score.py --dataset "$ds" --parser drain
done

echo "=== table ==="
uv run python scripts/make_table.py

if printf '%s\n' "${datasets[@]}" | grep -qx Apache; then
  uv run python scripts/verify_golden.py
fi

echo "=== tests ==="
uv run pytest -q

echo "done -> results/results.md"
