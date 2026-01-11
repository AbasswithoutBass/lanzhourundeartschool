#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${1:-8000}"
PID_FILE="${ROOT_DIR}/.site_httpserver_${PORT}.pid"

stopped=false

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "Stopping static server (pid=$PID)"
    kill "$PID" 2>/dev/null || true
    sleep 0.2
    kill -9 "$PID" 2>/dev/null || true
    stopped=true
  fi
  rm -f "$PID_FILE" || true
fi

# Fallback: kill anything listening on the port
if lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Killing processes listening on port $PORT"
  lsof -tiTCP:"$PORT" -sTCP:LISTEN | xargs -I{} kill -9 {} 2>/dev/null || true
  stopped=true
fi

if [[ "$stopped" == false ]]; then
  echo "No static server found to stop on port $PORT."
fi
