@echo off
if not exist ".env" (
    echo ERROR: .env file not found. Create one with GIT_REPO_URL and GIT_PAT before starting.
    exit /b 1
)

docker compose up --build -d
docker compose logs --tail 100 mes-wrapper
