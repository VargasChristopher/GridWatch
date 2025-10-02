import base64
import json
import logging
import google.cloud.logging
from traffic_coordinator import get_traffic_digest
from pubsub import publish_messages

project_id = "namm-omni-dev"

def runTrafficUpdateAgent(cloudevent):
    """
    Cloud Function entry point to handle Pub/Sub messages.
    """
    client = google.cloud.logging.Client()
    client.setup_logging()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("cloud event data type: %s", type(cloudevent.data))
    logger.info("Received cloudevent data: %s", cloudevent.data)
    message = base64.b64decode(cloudevent.data["message"]["data"]).decode("utf-8")
    payload = json.loads(message)
    # Extract location and areas from the payload
    lat = payload.get("lat")
    lon = payload.get("lon")
    areas = payload.get("areas", [])
    
    # Generate the prompt for traffic information
    
    example_prompt = (
        f"My current location is {lat}, {lon}. Provide traffic information for the current time in "
        f"{areas} including all data from BBMP, BTP, social media, and weather."
    )
    logger.info("sending prompt to gemini: %s", example_prompt)
    # Get the traffic digest based on the generated prompt
    digest = get_traffic_digest(example_prompt)
    logging.info("Traffic digest generated:\n%s", digest)   
    # Convert the digest to JSON and publish it
    try:
        response = json.dumps(digest.model_dump(), indent=2)
    except json.JSONDecodeError:
        publish_messages(digest.model_dump(), lambda e: logging.error(f"Error publishing message: {e}"))
        return '', 200
    # Publish the response to Pub/Sub
    publish_messages(response, lambda e: logging.error(f"Error publishing message: {e}"))
    return '', 200