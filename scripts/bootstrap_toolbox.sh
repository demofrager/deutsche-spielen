#!/usr/bin/env bash
# Creates and provisions the deutsche-spielen distrobox (first-run or repair).
set -euo pipefail

BOX_NAME="${1:-deutsche-spielen-toolbox}"
IMAGE="registry.fedoraproject.org/fedora-toolbox:latest"
PROJECT_DIR="/var/home/demofrager/code/deutsche_spielen"
VENV_PATH="/var/home/demofrager/code/.venv-deutsche"

if ! command -v distrobox >/dev/null 2>&1; then
  echo "distrobox is required but was not found on PATH."
  exit 1
fi

if distrobox list | awk -F'|' '{print $2}' | tr -d ' ' | grep -qx "$BOX_NAME"; then
  echo "Distrobox '$BOX_NAME' already exists, skipping creation."
else
  echo "Creating distrobox '$BOX_NAME'..."
  distrobox create --yes --image "$IMAGE" --name "$BOX_NAME"
fi

echo "Installing system packages inside '$BOX_NAME'..."
distrobox enter "$BOX_NAME" -- sh -lc '
  set -e
  sudo dnf -y install python3 python3-pip python3-virtualenv
'

echo "Installing Python dependencies inside '$BOX_NAME'..."
distrobox enter "$BOX_NAME" -- sh -lc "
  set -e

  VENV_PATH=${VENV_PATH}
  PROJECT_DIR=${PROJECT_DIR}

  if [[ ! -x \"\$VENV_PATH/bin/python\" ]]; then
    python3 -m venv \"\$VENV_PATH\"
  fi

  \"\$VENV_PATH/bin/python\" -m pip install --upgrade pip
  \"\$VENV_PATH/bin/pip\" install -r \"\$PROJECT_DIR/requirements.txt\"
"

echo ""
echo "Bootstrap complete. Run the app with: ./run.sh run_local"
