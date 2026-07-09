#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN=${1-python3}
VENV_DIR=${2-venv}

echo "Creating virtualenv in ${VENV_DIR} using ${PYTHON_BIN}"
${PYTHON_BIN} -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Virtualenv created and dependencies installed. Activate with: source ${VENV_DIR}/bin/activate"
