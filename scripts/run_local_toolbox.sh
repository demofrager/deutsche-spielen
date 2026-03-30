#!/usr/bin/env bash
# Runs the FastAPI dev server inside the deutsche-spielen distrobox.
set -euo pipefail

BOX_NAME="${1:-deutsche-spielen-toolbox}"
APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8001}"
PROJECT_DIR="/var/home/demofrager/code/deutsche_spielen"
VENV_PYTHON="/var/home/demofrager/code/.venv-deutsche/bin/python"

if ! command -v distrobox >/dev/null 2>&1; then
  echo "distrobox is required but was not found on PATH."
  exit 1
fi

if ! distrobox list | awk -F'|' '{print $2}' | tr -d ' ' | grep -qx "$BOX_NAME"; then
  echo "Distrobox '$BOX_NAME' not found. Run './run.sh setup' first."
  exit 1
fi

echo "Starting Deutsche Spielen at http://${APP_HOST}:${APP_PORT}"
distrobox enter "$BOX_NAME" -- sh -lc "
  set -e
  cd ${PROJECT_DIR}

  if ! ${VENV_PYTHON} -c 'import fastapi' >/dev/null 2>&1; then
    echo 'Dependencies missing, installing...'
    ${VENV_PYTHON} -m pip install -r requirements.txt
  fi

  ${VENV_PYTHON} -m uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload
"
