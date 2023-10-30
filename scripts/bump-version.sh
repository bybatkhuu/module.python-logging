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

# Loading .env file:
if [ -f ".env" ]; then
	# shellcheck disable=SC1091
	source .env
fi
## --- Base --- ##


## --- Variables --- ##
# Load from envrionment variables:
VERSION_FILE="${VERSION_FILE:-beans_logging/__version__.py}"


_BUMP_TYPE=""

# Flags:
_IS_PUSH_TAG=false
## --- Variables --- ##


## --- Main --- ##
main()
{
	## --- Menu arguments --- ##
	if [ -n "${1:-}" ]; then
		for _input in "${@:-}"; do
			case ${_input} in
				-b=* | --bump-type=*)
					_BUMP_TYPE="${_input#*=}"
					shift;;
				-p | --push-tag)
					_IS_PUSH_TAG=true
					shift;;
				*)
					echoError "Failed to parsing input -> ${_input}"
					echoInfo "USAGE: ${0}  -b=*, --bump-type=* [major | minor | patch] | -p, --push-tag"
					exit 1;;
			esac
		done
	fi
	## --- Menu arguments --- ##


	if [ -z "${_BUMP_TYPE:-}" ]; then
		echoError "Bump type is empty! Use '-b=' or '--bump-type=' argument."
		exit 1
	fi

	if [ "${_BUMP_TYPE}" != "major" ] && [ "${_BUMP_TYPE}" != "minor" ] && [ "${_BUMP_TYPE}" != "patch" ]; then
		echo "Bump type '${_BUMP_TYPE}' is invalid, should be: 'major', 'minor' or 'patch'!"
		exit 1
	fi

	if [ "${_IS_PUSH_TAG}" == true ]; then
		exitIfNoGit
	fi


	echoInfo "Checking current version..."
	_current_version="$(./scripts/get-version.sh)"
	echoOk "Current version: '${_current_version}'"

	# Split the version string into its components:
	_major=$(echo "${_current_version}" | cut -d. -f1)
	_minor=$(echo "${_current_version}" | cut -d. -f2)
	_patch=$(echo "${_current_version}" | cut -d. -f3)

	_new_version=${_current_version}
	# Determine the new version based on the type of bump:
	if [ "${_BUMP_TYPE}" == "major" ]; then
		_new_version="$((_major + 1)).0.0"
	elif [ "${_BUMP_TYPE}" == "minor" ]; then
		_new_version="${_major}.$((_minor + 1)).0"
	elif [ "${_BUMP_TYPE}" == "patch" ]; then
		_new_version="${_major}.${_minor}.$((_patch + 1))"
	fi

	echoInfo "Bumping version to '${_new_version}'..."
	# Update the version file with the new version:
	echo -e "# -*- coding: utf-8 -*-\n\n__version__ = \"${_new_version}\"" > "${VERSION_FILE}" || exit 2
	echoOk "New version: '${_new_version}'"

	if [ "${_IS_PUSH_TAG}" == true ]; then
		echoInfo "Pushing git tag 'v${_new_version}'..."
		if git rev-parse "v${_new_version}" > /dev/null 2>&1; then
			echoError "'v${_new_version}' tag is already exists."
			exit 1
		else
			# Commit the updated version file:
			git add "${VERSION_FILE}" || exit 2
			git commit -m ":bookmark: Bump version to '${_new_version}'." || exit 2
			git push || exit 2

			git tag "v${_new_version}" || exit 2
			# git push origin "v${_new_version}" || exit 2
			# shellcheck disable=SC1083
			git push "$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream} | sed 's/\/.*//')" "v${_new_version}" || exit 2
		fi
		echoOk "Done."
	fi
}

main "${@:-}"
## --- Main --- ##
