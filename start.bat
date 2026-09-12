@echo off
if not exist ".env" (
    echo ERROR: .env file not found. Create one with GIT_REPO_URL and GIT_PAT before starting.
    exit /b 1
)

for /f %%i in ('docker compose ps -q mes-wrapper') do set CONTAINER_ID=%%i

if defined CONTAINER_ID (
    echo Service already running, restarting...
    docker compose restart mes-wrapper
) else (
    docker compose up --build -d
)

docker compose logs --tail 100 mes-wrapper
