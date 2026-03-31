#!/usr/bin/env bash
# Runs the FastAPI dev server inside the deutsche-spielen distrobox.
set -euo pipefail

BOX_NAME="${1:-deutsche-spielen-toolbox}"
APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8001}"
LANGUAGETOOL_PORT="${LANGUAGETOOL_PORT:-8081}"
ENABLE_LANGUAGETOOL="${ENABLE_LANGUAGETOOL:-1}"
LANGUAGETOOL_VERSION="${LANGUAGETOOL_VERSION:-6.4}"
PROJECT_DIR="/var/home/demofrager/code/deutsche_spielen"
VENV_PYTHON="/var/home/demofrager/code/.venv-deutsche/bin/python"
LT_DIR="/var/home/demofrager/code/.cache/languagetool"
LT_ARCHIVE="LanguageTool-${LANGUAGETOOL_VERSION}.zip"
LT_URL="https://languagetool.org/download/${LT_ARCHIVE}"
LT_HOME="${LT_DIR}/LanguageTool-${LANGUAGETOOL_VERSION}"
LT_PID_FILE="${LT_DIR}/languagetool.pid"
LT_LOG_FILE="${LT_DIR}/languagetool.log"

if ! command -v distrobox >/dev/null 2>&1; then
  echo "distrobox is required but was not found on PATH."
  exit 1
fi

if ! distrobox list | awk -F'|' '{print $2}' | tr -d ' ' | grep -qx "$BOX_NAME"; then
  echo "Distrobox '$BOX_NAME' not found. Run './run.sh setup' first."
  exit 1
fi

if [[ "$ENABLE_LANGUAGETOOL" == "1" ]]; then
  distrobox enter "$BOX_NAME" -- sh -lc "
    set -e

    mkdir -p '${LT_DIR}'

    if [ ! -d '${LT_HOME}' ]; then
      if [ ! -f '${LT_DIR}/${LT_ARCHIVE}' ]; then
        echo 'Downloading LanguageTool ${LANGUAGETOOL_VERSION}...'
        curl -fL '${LT_URL}' -o '${LT_DIR}/${LT_ARCHIVE}'
      fi

      echo 'Extracting LanguageTool...'
      unzip -o '${LT_DIR}/${LT_ARCHIVE}' -d '${LT_DIR}' >/dev/null
    fi

    if [ -f '${LT_PID_FILE}' ] && kill -0 \"\$(cat '${LT_PID_FILE}')\" >/dev/null 2>&1; then
      echo 'LanguageTool already running in distrobox.'
    else
      echo 'Starting LanguageTool in distrobox on port ${LANGUAGETOOL_PORT}...'
      nohup java -cp '${LT_HOME}/languagetool-server.jar' org.languagetool.server.HTTPServer --port ${LANGUAGETOOL_PORT} --allow-origin '*' >'${LT_LOG_FILE}' 2>&1 &
      echo \$! > '${LT_PID_FILE}'
    fi

    echo 'Waiting for LanguageTool health endpoint...'
    for i in \$(seq 1 45); do
      if curl -fsS 'http://127.0.0.1:${LANGUAGETOOL_PORT}/v2/languages' >/dev/null 2>&1; then
        echo 'LanguageTool is ready at http://127.0.0.1:${LANGUAGETOOL_PORT}'
        exit 0
      fi
      sleep 1
    done

    echo 'LanguageTool did not become ready in time.'
    exit 1
  "
fi

echo "Starting Deutsche Spielen at http://${APP_HOST}:${APP_PORT}"
distrobox enter "$BOX_NAME" -- sh -lc "
  set -e
  cd ${PROJECT_DIR}

  if ! ${VENV_PYTHON} -c 'import fastapi' >/dev/null 2>&1; then
    echo 'Dependencies missing, installing...'
    ${VENV_PYTHON} -m pip install -r requirements.txt
  fi

  export LANGUAGETOOL_URL='http://127.0.0.1:${LANGUAGETOOL_PORT}'
  ${VENV_PYTHON} -m uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload
"
