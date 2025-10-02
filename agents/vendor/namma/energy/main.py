"""
orca.py – CLI launcher for BESCOMOutageAgent.
"""

import json
import logging
from energy_coordinator import get_energy_digest
from pubsub import publish_messages
# from flask import Flask
import base64

project_id = "namm-omni-dev"

# app = Flask(__name__)


# @app.get("/health")
# def health_check():
#     return {"status": "ok"}

def run_energy_management_agent(cloudevent):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("cloud event data type: %s", type(cloudevent.data))
    logger.info("Received cloudevent data: %s", cloudevent.data)
    message = base64.b64decode(cloudevent.data["message"]["data"]).decode("utf-8")
    payload = json.loads(message)
    lat = payload.get("lat")
    lon = payload.get("lon")
    areas = payload.get("areas", [])
    example_prompt = (
        f"My location is {lat}, {lon}. Provide power-outage information for the next 24 hours in "
        f"{areas} including official BESCOM notices "
        "and reliable local news reports."
    )
    digest = get_energy_digest(example_prompt)
    try:
        payload = json.dumps(digest.model_dump(), indent=2)
    except json.JSONDecodeError:
        logging.error("Unable to parse model response, publishing digest %s",digest.model_dump())
        publish_messages(digest.model_dump(),lambda e: logger.error("Pub/Sub error: %s", e))
        return '',200
    logger.info("Energy digest generated:\n%s", payload)
    # Publish to Pub/Sub (comment out if running locally without GCP creds)
    try:
        publish_messages(payload, lambda e: logger.error("Pub/Sub error: %s", e))
    except Exception as e:
        logger.error("Publish skipped – %s", e)
    return '', 200