import logging
import os

import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger("API-PC")


def send_to_mes(path: str, payload: dict) -> Response:
    base_url = os.environ["MES_BASE_URL"]
    token = os.environ["MES_API_TOKEN"]
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(url=url, json=payload, headers=headers, timeout=10.0)

        try:
            body = response.json()
        except ValueError:
            body = response.text

        logger.info(f"MES responded with status {response.status_code}.")
        if isinstance(body, (dict, list)):
            return JSONResponse(content=body, status_code=response.status_code)
        return Response(content=body, status_code=response.status_code)

    except requests.exceptions.Timeout:
        logger.error("Connection to MES API timed out.")
        raise HTTPException(
            status_code=504,
            detail={
                "status": "FAILED",
                "message": "Gateway Timeout: MES API did not respond in time.",
            },
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to MES API: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail={
                "status": "FAILED",
                "message": f"Bad Gateway: Unable to reach MES API. Error: {str(e)}",
            },
        )


def receive_from_mes(path: str) -> Response:
    base_url = os.environ["MES_BASE_URL"]
    token = os.environ["MES_API_TOKEN"]
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.get(url=url, headers=headers, timeout=10.0)

        try:
            body = response.json()
        except ValueError:
            body = response.text

        logger.info(f"MES responded with status {response.status_code}.")
        if isinstance(body, (dict, list)):
            return JSONResponse(content=body, status_code=response.status_code)
        return Response(content=body, status_code=response.status_code)

    except requests.exceptions.Timeout:
        logger.error("Connection to MES API timed out.")
        raise HTTPException(
            status_code=504,
            detail={
                "status": "FAILED",
                "message": "Gateway Timeout: MES API did not respond in time.",
            },
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to MES API: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail={
                "status": "FAILED",
                "message": f"Bad Gateway: Unable to reach MES API. Error: {str(e)}",
            },
        )

