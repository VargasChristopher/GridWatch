# Emergency Agent for GridWatch

Emergency monitoring agent for GridWatch that provides comprehensive real-time awareness of emergency situations including road closures, emergency services operations, and public alerts.

## Features

### 🛣️ Roads Emergency Monitoring
- Road closures and lane restrictions
- Traffic accidents and hazardous conditions
- Emergency vehicle operations affecting traffic
- Highway emergency situations
- Construction/infrastructure emergencies
- Weather-related road impacts
- Department of Transportation alerts

### 🚑 Emergency Services Tracking
- Active emergency calls (police, fire, medical)
- Emergency service dispatch patterns
- Ambulance operations and status
- Fire truck responses
- Police operations
- Mutual aid responses
- Hospital emergency department status
- Hazmat response activities
- Search and rescue operations

### 📢 Public Emergency Alerts
- Amber Alerts and Silver Alerts
- Evacuation orders
- Shelter-in-place orders
- Emergency management agency alerts
- Official emergency declarations
- Civil emergencies
- Utility emergencies
- Public safety notices

## Architecture

The Emergency Agent consists of three specialized sub-agents:

1. **Roads Emergency Agent** - Monitors road conditions and traffic emergencies
2. **Escorts Emergency Agent** - Tracks emergency services operations
3. **Public Alerts Agent** - Aggregates official emergency alerts

All agents run in parallel and results are merged into a unified emergency digest.

## Data Sources

### Official Agencies (Highest Priority)
- Department of Transportation (DOT)
- City Emergency Management
- Police Department
- Fire/Rescue services
- Emergency Management Agency
- 911 Dispatch centers
- National Weather Service

### Verified Sources
- News organizations
- Traffic apps (Waze, Google Maps)
- Emergency service social media
- Official alert systems

### Community Sources
- Citizen reports
- Social media (verified)

## Severity Scale

```
🔴 Critical (1.0)  - Multi-fatality incidents, major disasters
🟠 High (0.8)      - Significant emergencies, major road closures
🟡 Medium (0.5)    - Moderate impact emergencies
🟢 Low (0.2)       - Minor incidents, advisories
```

## Confidence Scoring

Confidence ranges from 0.0 (low trust) to 1.0 (official agency):
- Official sources: 0.95-1.0
- Verified emergency services: 0.85-0.95
- News/verified sources: 0.6-0.8
- Community reports: 0.3-0.6

## Installation

### Prerequisites
- Python 3.11+
- Google Gemini API key
- pip

### Setup
```bash
# Navigate to agent directory
cd /workspaces/GridWatch/agents/vendor/namma/emergency

# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your-google-api-key"
```

## Usage

### Standalone Execution
```bash
python __main__.py "Show active emergencies in Washington DC"
python __main__.py "What emergency services are responding?"
python __main__.py "Are there any evacuation orders?"
python __main__.py "Show road closures in downtown"
```

### As Google Cloud Function
```bash
gcloud functions deploy emergency_agent \
  --runtime python311 \
  --trigger-topic emergency-agent-topic \
  --entry-point run_emergency \
  --set-env-vars GOOGLE_API_KEY=<your-key>
```

### In GridWatch Orchestrator
```bash
cd /workspaces/GridWatch/gridwatch_agents/src
python run_orchestrator.py
```

## Output Format

```json
{
  "emergency_digest": [
    {
      "type": "road_closure|emergency_escort|public_alert",
      "severity": 0.0-1.0,
      "confidence": 0.0-1.0,
      "location": "Street name, city",
      "lat": 38.8951,
      "lng": -77.0367,
      "description": "Detailed description",
      "source": "Agency or news outlet",
      "updated_at": "ISO 8601 timestamp"
    }
  ]
}
```

## Integration with GridWatch

The Emergency Agent integrates seamlessly with GridWatch's multi-incident system:

- **Configuration**: `/workspaces/GridWatch/gridwatch_config/agents/emergency_agent.yaml`
- **Schema**: All incidents conform to GridWatch unified schema
- **Orchestration**: Runs in parallel with traffic, outage, and crime agents
- **Aggregation**: Results merged with deduplication (200m radius, 15min window)

## Model Configuration

By default, the agent uses `gemini-2.5-flash` for optimal performance:
- Fast response times
- Cost-effective
- High free tier limits
- Excellent accuracy

Override with environment variable:
```bash
export EMERGENCY_AGENT_MODEL="gemini-2.5-pro"
```

## Error Handling

The agent includes robust error handling:
- Failed sub-agent calls noted but don't block other results
- Low confidence scores for incomplete data
- Graceful degradation with fallback information
- Detailed logging for debugging

## Performance

- **Response Time**: 5-15 seconds typical
- **Parallel Execution**: All 3 sub-agents run simultaneously
- **Scalability**: Cloud Functions ready
- **Reliability**: Async/await with proper error handling

## Documentation

- [GridWatch Integration](../environment/GRIDWATCH_INTEGRATION.md)
- [Architecture](../../COMPLETE_ARCHITECTURE.md)

## Support

For issues or questions:
1. Check agent README.md
2. Review COMPLETE_ARCHITECTURE.md
3. Check error logs for details
4. Verify API key is configured
