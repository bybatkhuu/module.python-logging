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
## --- Base --- ##


## --- Main --- ##
main()
{
	echoInfo "Cleaning..."

	find . -type f -name ".DS_Store" -print -delete || exit 2
	find . -type f -name ".Thumbs.db" -print -delete || exit 2
	find . -type d -name "__pycache__" -exec rm -rfv {} + || exit 2
	# find . -type d -name "logs" -exec rm -rfv {} + || exit 2

	rm -rfv ./examples/simple/logs || exit 2
	rm -rfv ./examples/advanced/logs || exit 2
	rm -rfv .benchmarks || exit 2
	rm -rfv .pytest_cache || exit 2
	rm -rfv build || exit 2
	rm -rfv dist || exit 2
	# rm -rfv ./*.egg-info || exit 2
	rm -rfv .coverage || exit 2

	echoOk "Done."
}

main "${@:-}"
## --- Main --- ##
