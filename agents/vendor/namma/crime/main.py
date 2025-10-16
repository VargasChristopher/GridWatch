import base64
import json
import logging
import google.cloud.logging
from crime_coordinator import get_crime_digest
from pubsub import publish_messages

project_id = "namm-omni-dev"

def runCrimeMonitoringAgent(cloudevent):
    """
    Cloud Function entry point to handle Pub/Sub messages for crime monitoring.
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
    timeframe = payload.get("timeframe", "last 24 hours")
    crime_types = payload.get("crime_types", "all")
    
    # Generate the prompt for crime information
    example_prompt = (
        f"My current location is {lat}, {lon}. Provide crime and safety information for "
        f"{areas} from the {timeframe}. Focus on {crime_types} crime types. "
        f"Include all data from police reports, news sources, and social media."
    )
    
    logger.info("sending prompt to gemini: %s", example_prompt)
    
    # Get the crime digest based on the generated prompt
    digest = get_crime_digest(example_prompt)
    logging.info("Crime digest generated:\n%s", digest)
    
    # Convert the digest to JSON and publish it
    try:
        response = json.dumps(digest.model_dump(), indent=2)
    except json.JSONDecodeError:
        publish_messages(digest.model_dump(), lambda e: logging.error(f"Error publishing message: {e}"))
        return '', 200
    
    # Publish the response to Pub/Sub
    publish_messages(response, lambda e: logging.error(f"Error publishing message: {e}"))
    return '', 200
