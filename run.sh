#!/bin/bash
# Launch the Rodent Object Exploration Scorer.
# Double-click this file from Finder, or run ./run.sh from a terminal.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment (first run only)…"
    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python app.py
