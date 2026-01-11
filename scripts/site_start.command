#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${1:-8000}"
PID_FILE="${ROOT_DIR}/.site_httpserver_${PORT}.pid"
LOG_FILE="${ROOT_DIR}/.site_httpserver_${PORT}.log"

# If pidfile exists and process is alive, reuse it
if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "Static server already running (pid=$PID, port=$PORT)."
    open "http://localhost:${PORT}/" || true
    exit 0
  fi
fi

# If port is already in use, just open it.
if lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use; opening http://localhost:${PORT}/"
  open "http://localhost:${PORT}/" || true
  exit 0
fi

echo "Starting static server at http://localhost:${PORT}/"

# Start in background and record pid
# Use python3 from PATH; users can override by exporting PYTHON
PYTHON_BIN="${PYTHON:-python3}"
nohup "$PYTHON_BIN" -m http.server "$PORT" --bind 127.0.0.1 >"$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

echo "pid=$SERVER_PID"
echo "log=$LOG_FILE"

# Give it a brief moment, then open
sleep 0.2
open "http://localhost:${PORT}/" || true
