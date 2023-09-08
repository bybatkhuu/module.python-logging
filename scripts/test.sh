#!/bin/bash
set -euo pipefail

## --- Base --- ##
# Getting path of this script file:
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
_PROJECT_DIR="$(cd "${_SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"
cd "${_PROJECT_DIR}" || exit 2

# Loading base script:
# shellcheck disable=SC1091
source ./scripts/base.sh


if [ -z "$(which python)" ]; then
	echoError "Python not found or not installed."
	exit 1
fi

if [ -z "$(which pytest)" ]; then
	echoError "Pytest not found or not installed."
	exit 1
fi
## --- Base --- ##


echoInfo "Running test..."
python -m pytest -sv || exit 2
# python -m pytest -sv -o log_cli=true || exit 2
# python -m pytest -sv --cov -o log_cli=true || exit 2
echoOk "Done."
