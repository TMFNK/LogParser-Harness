#!/usr/bin/env bash
# Drain-only is the stranger path. --with-trail also runs the sibling plugin.
# Usage: ./reproduce.sh --drain-only
#        ./reproduce.sh --drain-only Apache Linux
#        ./reproduce.sh --with-trail
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "usage: $0 --drain-only [Apache] [Linux] [OpenSSH]"
  echo "       $0 --with-trail"
  echo "Drain-only is the default stranger path. --with-trail needs ../LogParser-Trail."
  exit 0
fi

mode="${1:-}"
if [[ "$mode" != "--drain-only" && "$mode" != "--with-trail" ]]; then
  echo "Run: ./reproduce.sh --drain-only" >&2
  echo "Trail sibling: ./reproduce.sh --with-trail" >&2
  exit 2
fi
shift

if [[ "$mode" == "--with-trail" ]]; then
  datasets=(Apache)
else
  datasets=("$@")
  if [[ ${#datasets[@]} -eq 0 ]]; then
    datasets=(Apache)
  fi
fi

echo "=== env ==="
uv sync --frozen --extra dev

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
  slug="$(printf '%s' "$ds" | tr '[:upper:]' '[:lower:]')"
  uv run python scripts/verify_golden.py \
    --expected "expected/drain_${slug}_2k.json" \
    --actual "results/raw/drain_${slug}_scores.json"
done

if [[ "$mode" == "--with-trail" ]]; then
  echo "=== trail + score ==="
  uv run python scripts/run_trail.py --dataset Apache
  uv run python scripts/score.py --dataset Apache --parser trail
  uv run python scripts/verify_golden.py \
    --expected expected/trail_apache_2k.json \
    --actual results/raw/trail_apache_scores.json
  dataset_src="${DATASET_SRC:-../LogParser-Dataset}"
  if [ -f "$dataset_src/dataset/SecOps_2k.log" ]; then
    echo "=== trail SecOps-2k ==="
    uv run python scripts/run_trail.py --dataset SecOps
    uv run python scripts/verify_golden.py \
      --expected expected/trail_secops_2k.json \
      --actual results/raw/trail_secops_scores.json
  else
    echo "(skip SecOps-2k: $dataset_src not found)"
  fi
fi

echo "=== table ==="
uv run python scripts/make_table.py

echo "=== tests ==="
uv run pytest -q

echo "done -> results/results.md"
