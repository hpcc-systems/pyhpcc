#!/bin/bash
set -euo pipefail

POETRY_HOME="${POETRY_HOME:-${RUNNER_TEMP:-/tmp}/pyhpcc-poetry}"
POETRY="${POETRY:-$POETRY_HOME/bin/poetry}"

python3 -m venv "$POETRY_HOME"
"$POETRY_HOME/bin/python" -m pip install poetry==1.8.3
"$POETRY" install --with dev,coverage --no-interaction

if [[ -n "${GITHUB_ENV:-}" ]]; then
    printf 'POETRY_HOME=%s\nPOETRY=%s\n' "$POETRY_HOME" "$POETRY" >> "$GITHUB_ENV"
fi