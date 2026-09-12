import logging
import os
import json
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
        #"Authorization": f"Bearer {token}",
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

    # headers = {
    #     "Authorization": f"Bearer {token}",
    # }
    headers = None

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

def validate_serial_number(payload: dict, target_sn: str, program_name: str) -> bool:

    if not isinstance(payload, dict) or not payload.get("success"):
        return False

    records = payload.get("data", [])
    if not records:
        return False

    matching_parent = [r for r in records if r.get("serial_number") == target_sn]
    if not matching_parent:
        return False

    child_sns = [
        r.get("component_id") 
        for r in records 
        if r.get("component_id") and r.get("component_id") != "YES"
    ]
    if len(child_sns) != 4:
        return False

    has_grade_label = any(
        "Ensure the grade label" in r.get("ref_designator", "")
        for r in records
    )
    if not has_grade_label:
        return False

    yes_records = [r for r in records if r.get("component_id") == "YES"]
    required_labels = {"A", "B", "C", "D"}
    found_labels = set()

    for rec in yes_records:
        ref_text = rec.get("ref_designator", "").upper()
        for label in required_labels:
            if f"LABEL {label}" in ref_text or f"GRADE {label}" in ref_text or label in ref_text.split():
                found_labels.add(label)

    if found_labels != required_labels:
        return False

    return True


def verify_unit_children_from_mes(serial_number: str, program_name: str) -> bool:
  
    path = f"mes-api/p5599dc1uat/units/{serial_number}/children"
    
    response = receive_from_mes(path)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch data for {serial_number}. Status: {response.status_code}")
        return False
        
    try:
        payload = json.loads(response.body.decode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return False

    return validate_serial_number(payload, target_sn=serial_number, program_name=program_name)