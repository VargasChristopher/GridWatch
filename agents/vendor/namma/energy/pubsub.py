"""Publishes a JSON message to a Pub/Sub topic with an error handler."""
from google.cloud import pubsub_v1
from typing import Callable
import json

project_id = "namm-omni-dev"
topic_id = "energy-management-data"
subscription_id = "trigger-energy-management-agent-sub"
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
        
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()
    
def recieve_messages() -> str:
    """Pull a single message from the Pub/Sub subscription, acknowledge it, and return its data."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)



    # Pull one message synchronously
    response = subscriber.pull(subscription=subscription_path, max_messages=1, timeout=timeout)
    if not response.received_messages:
        raise RuntimeError("No messages received within timeout period")

    received = response.received_messages[0]
    message = received.message

    # Acknowledge the message to prevent redelivery
    subscriber.acknowledge(subscription=subscription_path, ack_ids=[received.ack_id])

    # Return the decoded message data
    return message.data.decode("utf-8")
