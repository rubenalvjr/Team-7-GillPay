#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv_local"
PY="$VENV/bin/python"

# Create venv if missing
if [ ! -x "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$VENV"
  else
    echo "Python 3 is required. Install Python 3 and try again." >&2
    exit 1
  fi
  "$PY" -m pip install --upgrade pip setuptools wheel
fi

# Install deps
if [ -f requirements.txt ]; then
  "$PY" -m pip install -r requirements.txt
else
  # Minimal runtime for fresh clones
  "$PY" -m pip install pandas matplotlib
fi

# Keep src/ imports and future pandas behavior consistent
export PYTHONPATH="$(pwd)"
export PANDAS_COPY_ON_WRITE=1

# Run as a module; pass through any args
exec "$PY" -m gui.app "$@"
