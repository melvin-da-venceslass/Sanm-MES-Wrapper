import logging
import os

import requests
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger("API-PC")


def _conduit_error_response(payload: dict, status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "source": payload.get("source", {}),
            "status": {"code": "ERROR", "message": message},
            "transaction_responses": [],
            "version": "1",
        },
    )


def send_to_conduit(payload: dict) -> Response:
    endpoint_url = os.environ["CONDUIT_URL"]
    token = os.environ["MES_API_TOKEN"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(
            url=endpoint_url, json=payload, headers=headers, timeout=10.0
        )

        try:
            body = response.json()
        except ValueError:
            body = response.text

        logger.info(f"Conduit responded with status {response.status_code}.")
        if isinstance(body, (dict, list)):
            return JSONResponse(content=body, status_code=response.status_code)
        return Response(content=body, status_code=response.status_code)

    except requests.exceptions.Timeout:
        logger.error("Connection to Conduit API timed out.")
        return _conduit_error_response(
            payload, 504, "Gateway Timeout: Conduit API did not respond in time."
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Conduit API: {str(e)}")
        return _conduit_error_response(
            payload, 502, f"Bad Gateway: Unable to reach Conduit API. Error: {str(e)}"
        )
