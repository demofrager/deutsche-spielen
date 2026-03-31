#!/usr/bin/env bash
# Runs project tests inside the deutsche-spielen distrobox.
set -euo pipefail

BOX_NAME="${1:-deutsche-spielen-toolbox}"
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

echo "Running tests in distrobox '$BOX_NAME'..."
distrobox enter "$BOX_NAME" -- sh -lc "
  set -e
  cd ${PROJECT_DIR}

  if ! ${VENV_PYTHON} -c 'import pytest' >/dev/null 2>&1; then
    echo 'Test dependencies missing, installing...'
    ${VENV_PYTHON} -m pip install -r requirements-dev.txt
  fi

  ${VENV_PYTHON} -m pytest
"
