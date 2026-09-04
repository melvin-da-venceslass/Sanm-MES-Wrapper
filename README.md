# Wrapper Service (MES & CONDUIT)

A FastAPI relay service that forwards requests to the MES API and the Conduit API.

## Setup

1. Create a virtual environment (once):
   ```
   python3 -m venv venv
   ```
2. Activate it and install dependencies:
   ```
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure `.env.prod` and `.env.uat` with the correct `CONDUIT_URL`, `MES_BASE_URL`, `CLIENT_ID`, `MES_API_TOKEN`, `HOST`, and `PORT` values.

## Running

- macOS/Linux:
  ```
  ./start_prod.sh
  ./start_uat.sh
  ```
- Windows:
  ```
  start_prod.bat
  start_uat.bat
  ```

Each starter script installs dependencies from `requirements.txt` and then starts the server in the matching environment (prod on port 8000, uat on port 8010 by default).
