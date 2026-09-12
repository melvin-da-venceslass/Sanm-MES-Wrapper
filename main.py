import argparse
import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from conduit_wrapper import send_to_conduit
from mes_wrapper import send_to_mes, receive_from_mes, verify_unit_children_from_mes

# Determine which environment (.env.prod / .env.uat) to load before anything
# else reads configuration from the environment. Falls back to APP_ENV so the
# app can also be launched via `uvicorn main:app` (e.g. with --workers).
# Only parse CLI args when run directly (`python main.py [env]`); when
# imported by uvicorn, sys.argv belongs to the uvicorn process itself.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper Service (MES & CONDUIT)")
    parser.add_argument(
        "env",
        nargs="?",
        default=os.environ.get("APP_ENV", "prod"),
        choices=["prod", "uat"],
        help="Environment to run in",
    )
    args, _ = parser.parse_known_args()
else:
    class _Args:
        env = os.environ.get("APP_ENV", "prod")

    args = _Args()

load_dotenv(f".env.{args.env}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API-PC")

app = FastAPI(title="Wrapper Service (MES & CONDUIT)", version="1.0")

START_TIME = time.time()


@app.get("/status")
async def status():
    return {
        "status": "online",
        "environment": args.env,
        "uptime_seconds": round(time.time() - START_TIME),
    }


@app.get("/", response_class=HTMLResponse)
async def welcome():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sanmina - MES Wrapper Service</title>
<style>
  body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .card { background: #1e293b; padding: 2.5rem 3rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); text-align: center; }
  h1 { margin: 0 0 0.25rem; font-size: 1.5rem; }
  .subtitle { color: #94a3b8; margin-bottom: 1.5rem; }
  .status { display: inline-flex; align-items: center; gap: 0.5rem; font-weight: bold; font-size: 1.1rem; }
  .dot { width: 12px; height: 12px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 8px #22c55e; }
  .dot.offline { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
  .meta { margin-top: 1rem; color: #64748b; font-size: 0.9rem; }
</style>
</head>
<body>
  <div class="card">
    <h1>Sanmina</h1>
    <div class="subtitle">MES Wrapper Service</div>
    <div class="status"><span class="dot" id="dot"></span><span id="statusText">Checking...</span></div>
    <div class="meta" id="meta"></div>
  </div>
<script>
async function refreshStatus() {
  const dot = document.getElementById('dot');
  const statusText = document.getElementById('statusText');
  const meta = document.getElementById('meta');
  try {
    const res = await fetch('/status');
    const data = await res.json();
    dot.classList.remove('offline');
    statusText.textContent = 'Online';
    meta.textContent = `Environment: ${data.environment} | Uptime: ${data.uptime_seconds}s`;
  } catch (e) {
    dot.classList.add('offline');
    statusText.textContent = 'Offline';
    meta.textContent = '';
  }
}
refreshStatus();
setInterval(refreshStatus, 5000);
</script>
</body>
</html>
"""


@app.post("/conduit")
async def forward_to_conduit(payload: dict):
    return send_to_conduit(payload)


@app.post("/{path:path}")
async def forward_to_mes(path: str, payload: dict):
    return send_to_mes(path, payload)

@app.get("/{path:path}")
async def get_from_mes(path: str,):
    return receive_from_mes(path)

@app.get("/validate/{serial_number}")
async def validate_mes_unit(serial_number: str, program_name: str = "DEFAULT"):
    
    is_valid = verify_unit_children_from_mes(serial_number=serial_number, program_name=program_name)
    
    return {
        "serial_number": serial_number, 
        "program_name": program_name,
        "is_valid": is_valid
    }

if __name__ == "__main__":
    import os

    import uvicorn

    logger.info(f"Starting Wrapper Service (MES & CONDUIT) in '{args.env}' environment.")
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
    )