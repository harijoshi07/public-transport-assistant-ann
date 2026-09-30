#!/usr/bin/env bash
# Quick launch script for Public Transportation Assistance system

set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
elif [ -f "$ROOT_DIR/venv/bin/activate" ]; then
    source "$ROOT_DIR/venv/bin/activate"
fi

echo "======================================================"
echo " Starting Public Transportation Assistance System"
echo " Open your browser at: http://127.0.0.1:8000/"
echo " Press Ctrl+C to stop."
echo "======================================================"

python manage.py runserver 8000
