# ---------- main.py ----------
"""
Emergency Agent - Google Cloud Function entry point.

Deploy with:
  gcloud functions deploy emergency_agent \
    --runtime python311 \
    --trigger-topic emergency-agent-topic \
    --entry-point run_emergency \
    --set-env-vars GOOGLE_API_KEY=<your-key>
"""

import functions_framework
from google.cloud import pubsub_v1
import json
from emergency_coordinator import get_emergency_digest

@functions_framework.http
def run_emergency(request):
    """
    HTTP endpoint for the emergency agent.
    Receives a query and returns emergency digest.
    """
    try:
        request_json = request.get_json(silent=True)
        query = request_json.get('query', 'Show active emergencies') if request_json else 'Show active emergencies'
        
        result = get_emergency_digest(query)
        
        return {
            'status': 'success',
            'emergency_digest': result.emergency_digest
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500


@functions_framework.cloud_event
def emergency_agent_pubsub(cloud_event):
    """
    Pub/Sub topic handler for emergency agent.
    Processes messages from emergency-agent-topic.
    """
    import base64
    
    try:
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        message_data = json.loads(pubsub_message)
        query = message_data.get('query', 'Show active emergencies')
        
        result = get_emergency_digest(query)
        
        # Publish result to results topic
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(
            message_data.get('project_id'),
            'emergency-results'
        )
        
        result_message = {
            'source': 'emergency_agent',
            'query': query,
            'result': result.emergency_digest
        }
        
        publisher.publish(topic_path, json.dumps(result_message).encode('utf-8'))
        
        print(f"✅ Emergency agent processed: {query}")
        
    except Exception as e:
        print(f"❌ Error in emergency agent: {str(e)}")
        raise
