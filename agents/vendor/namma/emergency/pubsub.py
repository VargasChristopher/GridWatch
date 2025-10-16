# ---------- pubsub.py ----------
"""
Pub/Sub integration for Emergency Agent.

Publishes emergency digests to emergency-incidents topic for downstream processing.
"""

import json
from google.cloud import pubsub_v1

def publish_emergency_digest(project_id: str, digest: dict, topic_name: str = "emergency-incidents"):
    """
    Publish emergency digest to Pub/Sub topic.
    
    Args:
        project_id: GCP project ID
        digest: Emergency digest dictionary
        topic_name: Pub/Sub topic name
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    
    message_data = json.dumps(digest).encode('utf-8')
    future = publisher.publish(topic_path, message_data)
    
    message_id = future.result()
    print(f"✅ Emergency digest published with ID: {message_id}")
    
    return message_id


def get_emergency_subscriber(project_id: str, subscription_name: str = "emergency-incidents-sub"):
    """
    Create a subscriber for emergency incident messages.
    
    Args:
        project_id: GCP project ID
        subscription_name: Subscription name
        
    Returns:
        Subscriber client
    """
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    
    return subscriber, subscription_path
