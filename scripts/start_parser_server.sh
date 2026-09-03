#!/usr/bin/env bash
# Start/stop the llama.cpp server backing EFParser runs.
#
#   Parser LLM server :8090  Qwen3.8-2B-Q6_K (OpenAI-compatible /v1)
#
# Port 8090 (not 8080) so ee-case-studies servers can coexist.
# Binds 127.0.0.1 only — clients must use 127.0.0.1, never localhost.
#
# Usage: scripts/start_parser_server.sh [start|stop|status]
set -euo pipefail

LLAMA_SERVER="${LLAMA_SERVER:-/opt/homebrew/opt/llama.cpp/bin/llama-server}"
PORT="${PORT:-8090}"
ALIAS="${ALIAS:-qwen3.8-2b-q6k}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
PIDFILE="${ROOT_DIR}/logs/parser_server.pid"
LOGFILE="${ROOT_DIR}/logs/parser_server.log"
mkdir -p "${LOG_DIR}"

MODEL="${MODEL:-}"
if [[ -z "${MODEL}" ]]; then
  MODEL="/Users/edis-mac/.cache/huggingface/hub/models--empero-ai--Qwen3.8-2B-Distill-GGUF/snapshots/f4f73582d0b149595450c719b9a7521a03894f9c/Qwen3.8-2B-Q6_K.gguf"
fi

# Resolve HF snapshot symlink to the real blob file.
if [[ -e "${MODEL}" ]]; then
  MODEL="$(readlink -f "${MODEL}" 2>/dev/null || echo "${MODEL}")"
fi

if [[ ! -x "${LLAMA_SERVER}" ]]; then
  echo "error: llama-server not found at ${LLAMA_SERVER}" >&2
  echo "set LLAMA_SERVER=/path/to/llama-server to override" >&2
  exit 1
fi
if [[ ! -f "${MODEL}" ]]; then
  echo "error: model file missing: ${MODEL}" >&2
  echo "set MODEL=/path/to/model.gguf to override" >&2
  exit 1
fi

cmd="${1:-status}"
case "${cmd}" in
  start)
    if [[ -f "${PIDFILE}" ]] && kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
      echo "parser server already running (pid $(cat "${PIDFILE}"), port ${PORT})"
      exit 0
    fi
    rm -f "${PIDFILE}"
    echo "starting parser server on :${PORT} (alias=${ALIAS})"
    # -np 1 keeps KV-cache small on 8GB machines; -ngl 999 offloads to GPU (Metal).
    nohup "${LLAMA_SERVER}" \
      --model "${MODEL}" \
      --alias "${ALIAS}" \
      --host 127.0.0.1 \
      --port "${PORT}" \
      -ngl 999 \
      -np 1 \
      --ctx-size 4096 \
      >"${LOGFILE}" 2>&1 &
    echo $! >"${PIDFILE}"
    echo "waiting for readiness..."
    for _ in $(seq 1 30); do
      if curl -sf "127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
        echo "ready on 127.0.0.1:${PORT}"
        exit 0
      fi
      sleep 2
    done
    echo "error: server did not answer in 60s, see ${LOGFILE}" >&2
    exit 1
    ;;
  stop)
    if [[ -f "${PIDFILE}" ]] && kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
      kill "$(cat "${PIDFILE}")" && echo "stopped parser server (pid $(cat "${PIDFILE}"))"
      rm -f "${PIDFILE}"
    else
      echo "parser server not running"
      rm -f "${PIDFILE}"
    fi
    ;;
  status)
    if [[ -f "${PIDFILE}" ]] && kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
      echo "running (pid $(cat "${PIDFILE}"), port ${PORT})"
      curl -s "127.0.0.1:${PORT}/v1/models" | head -c 300; echo
    else
      echo "not running"
    fi
    ;;
  *)
    echo "usage: $0 [start|stop|status]" >&2
    exit 1
    ;;
esac
