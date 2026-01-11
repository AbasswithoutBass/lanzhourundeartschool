#!/bin/zsh
set -euo pipefail

# Always run from repo root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

PORT="${PORT:-5050}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
ADMIN_SECRET_KEY="${ADMIN_SECRET_KEY:-dev-secret}"

PY="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
  else
    PY="python"
  fi
fi

echo "== Admin server =="
echo "Root: $ROOT_DIR"
echo "Port: $PORT"
echo "Python: $PY"
echo "Login: password=$ADMIN_PASSWORD"
echo "Secret: $ADMIN_SECRET_KEY"
echo

# Free the port
(lsof -tiTCP:"$PORT" -sTCP:LISTEN | xargs -I{} kill -9 {} 2>/dev/null || true)

# Start
export ADMIN_PASSWORD
export ADMIN_SECRET_KEY

open "http://127.0.0.1:${PORT}/admin" >/dev/null 2>&1 || true

exec "$PY" admin_app/app.py
