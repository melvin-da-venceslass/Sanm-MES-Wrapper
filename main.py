import argparse
import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from conduit_wrapper import send_to_conduit
from mes_wrapper import send_to_mes, receive_from_mes

# Determine which environment (.env.prod / .env.uat) to load before anything
# else reads configuration from the environment.
parser = argparse.ArgumentParser(description="Wrapper Service (MES & CONDUIT)")
parser.add_argument("env", choices=["prod", "uat"], help="Environment to run in")
args, _ = parser.parse_known_args()

load_dotenv(f".env.{args.env}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API-PC")

app = FastAPI(title="Wrapper Service (MES & CONDUIT)", version="1.0")


@app.post("/conduit")
async def forward_to_conduit(payload: dict):
    return send_to_conduit(payload)


@app.post("/{path:path}")
async def forward_to_mes(path: str, payload: dict):
    return send_to_mes(path, payload)

@app.get("/{path:path}")
async def get_from_mes(path: str,):
    return receive_from_mes(path)

if __name__ == "__main__":
    import os

    import uvicorn

    logger.info(f"Starting Wrapper Service (MES & CONDUIT) in '{args.env}' environment.")
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
    )