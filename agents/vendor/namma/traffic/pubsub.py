"""Publishes a JSON message to a Pub/Sub topic with an error handler."""
from google.cloud import pubsub_v1
from typing import Callable
import json
from concurrent.futures import TimeoutError

project_id = "namm-omni-dev"
topic_id = "traffic-update-data"
subscription_id = "trigger-traffic-update-agent-sub"
timeout = 5000

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


def publish_messages(json_message: str, error_handler: Callable[[Exception], None]) -> None:
    try:
        # Optionally validate JSON input.
        parsed = json.dumps(json_message).encode("utf-8")
        # Publish the message as a byte string.
        future = publisher.publish(topic_path, data=parsed)
        message_id = future.result()  # Blocks until the message is published.
        print(f"Published message ID: {message_id}")
    except Exception as e:
        error_handler(e)