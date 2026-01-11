#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

PORT="${PORT:-5050}"

(lsof -tiTCP:"$PORT" -sTCP:LISTEN | xargs -I{} kill -9 {} 2>/dev/null || true)
echo "Stopped anything listening on port $PORT"
