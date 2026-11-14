#!/bin/sh
set -eu
APP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${BLOCKWERK_PYTHON:-}" ]; then
    PYTHON=$BLOCKWERK_PYTHON
elif command -v python3.12 >/dev/null 2>&1; then
    PYTHON=python3.12
elif command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    printf '%s\n' 'Python 3.12 is required. / Bitte Python 3.12 installieren.' >&2
    exit 1
fi
exec "$PYTHON" "$APP_DIR/tools/bootstrap.py" "$@"
