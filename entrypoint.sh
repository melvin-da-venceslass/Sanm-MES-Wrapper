#!/bin/sh
set -e

REPO_DIR="/app"
VENV_DIR="$REPO_DIR/.venv"

cd "$REPO_DIR"

# The bind-mounted repo is owned by the host user, not root inside the container.
git config --global --add safe.directory "$REPO_DIR"

if [ -d "$REPO_DIR/.git" ]; then
    echo "Pulling latest changes..."
    git pull
else
    echo "WARNING: $REPO_DIR is not a git repository, skipping git pull."
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

pip install --no-cache-dir -r requirements.txt

echo "Starting service (APP_ENV=${APP_ENV:-prod}, workers=${UVICORN_WORKERS:-10})..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${UVICORN_WORKERS:-10}"
