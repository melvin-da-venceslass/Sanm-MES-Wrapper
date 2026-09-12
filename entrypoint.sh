#!/bin/sh
set -e

REPO_DIR="/app"
VENV_DIR="$REPO_DIR/.venv"

cd "$REPO_DIR"

# The bind-mounted repo is owned by the host user, not root inside the container.
git config --global --add safe.directory "$REPO_DIR"

# GIT_REPO_URL/GIT_PAT allow authenticating against a private HTTPS remote
# (e.g. https://github.com/org/repo.git) without baking the token into the image.
if [ -n "$GIT_REPO_URL" ] && [ -n "$GIT_PAT" ]; then
    AUTH_REPO_URL=$(echo "$GIT_REPO_URL" | sed -E "s#https://#https://${GIT_USERNAME:-x-access-token}:${GIT_PAT}@#")
else
    AUTH_REPO_URL="$GIT_REPO_URL"
fi

if [ -d "$REPO_DIR/.git" ]; then
    if [ -n "$AUTH_REPO_URL" ]; then
        git remote set-url origin "$AUTH_REPO_URL"
    fi
    echo "Pulling latest changes..."
    git pull
elif [ -n "$AUTH_REPO_URL" ]; then
    echo "Cloning $GIT_REPO_URL..."
    git clone "$AUTH_REPO_URL" .
else
    echo "WARNING: $REPO_DIR is not a git repository and GIT_REPO_URL is not set, skipping git pull."
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
