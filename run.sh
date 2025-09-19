#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv_local"
PY="$VENV/bin/python"

# Create venv if missing
if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV"
  "$PY" -m pip install --upgrade pip setuptools wheel
fi

# Install deps
if [ -f requirements.txt ]; then
  "$PY" -m pip install -r requirements.txt
fi

# The two key lines for mac/Linux:
export PYTHONPATH="$(pwd)"   # <-- make 'src' resolvable
exec "$PY" -m gui.app        # <-- run as a module
