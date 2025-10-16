# Environment Monitoring Agent

## Overview

The Environment Monitoring Agent is part of the GridWatch system, designed to collect, analyze, and report environmental hazards and alerts from multiple sources. It provides real-time environmental intelligence to help residents and visitors stay informed about environmental conditions and prepare for potential hazards.

## Architecture

The agent uses a hierarchical multi-agent system:

### Coordinator
- **environment_coordinator**: Main orchestrator that aggregates data from all sub-agents and produces a unified environment digest

### Sub-Agents
1. **weather_agent**: Collects severe weather alerts and storm information
   - Severe thunderstorms, tornadoes, hurricanes
   - Blizzards, ice storms, extreme heat/cold
   - Wind advisories, hail warnings
   
2. **air_quality_agent**: Monitors air quality and pollution alerts
   - Air Quality Index (AQI) data
   - Wildfire smoke alerts
   - Pollution advisories
   - Sensitive group health warnings
   
3. **environmental_alerts_agent**: Tracks environmental hazards
   - Flood and flash flood warnings
   - Earthquake and seismic activity
   - Landslides and ground failures
   - Water contamination alerts
   - Tsunami warnings

## Features

- **Multi-Source Intelligence**: Aggregates data from official weather services, environmental agencies, geological surveys
- **Credibility Assessment**: Evaluates and prioritizes official sources over unverified reports
- **Cross-Verification**: Identifies hazards reported by multiple sources for higher confidence
- **Severity Scoring**: Assigns severity levels (Low, Medium, High, Critical) based on hazard type and magnitude
- **Time-Based Filtering**: Supports queries for specific time ranges
- **Location-Based**: Filters hazards by geographic area or region
- **Hazard Classification**: Categorizes environmental threats (weather, air quality, water, geological, other)

## Usage

### Direct Python Usage

```python
from environment_coordinator import get_environment_digest

# Query for environmental information
prompt = "Provide environmental hazard information for downtown area in the last 24 hours"
digest = get_environment_digest(prompt)

# Access the results
for hazard in digest.environment_digest:
    print(f"{hazard['timestamp']} - {hazard['location']}: {hazard['description']}")
```

### Cloud Function (Pub/Sub)

The agent can be deployed as a Google Cloud Function triggered by Pub/Sub messages:

```json
{
  "lat": 38.9072,
  "lon": -77.0369,
  "areas": ["Downtown", "National Park"],
  "timeframe": "last 24 hours",
  "hazard_types": "weather"
}
```

## Output Format

The agent produces a structured JSON output:

```json
{
  "environment_digest": [
    {
      "timestamp": "14:30 EST",
      "location": "Downtown area",
      "hazard_type": "Severe Thunderstorm",
      "severity": "High",
      "description": "Severe thunderstorm warning with large hail and damaging winds",
      "source": "National Weather Service",
      "advice": "Seek shelter indoors, avoid outdoor activities"
    },
    {
      "timestamp": "11:45 EST",
      "location": "Central zone",
      "hazard_type": "Air Quality",
      "severity": "Medium",
      "description": "Air quality index elevated (unhealthy for sensitive groups)",
      "source": "EPA Air Quality Monitor",
      "advice": "Vulnerable groups should limit outdoor exposure"
    }
  ]
}
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: API key for Google Gemini
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account credentials
- `project_id`: Google Cloud project ID (default: "namm-omni-dev")
- `topic_id`: Pub/Sub topic for environment updates (default: "environment-update-data")

## Data Sources

### Weather Services
- National Weather Service (NWS)
- NOAA meteorological data
- Weather.gov
- Storm tracking services

### Air Quality
- EPA AirNow
- State/local air quality agencies
- Wildfire smoke tracking
- Pollution monitoring networks

### Environmental Alerts
- USGS Earthquake Hazards Program
- NOAA flood and tsunami alerts
- Geological surveys
- Water quality agencies

## Hazard Classification

### Severity Levels
- **Low**: Minor weather changes, acceptable air quality, minor flooding
- **Medium**: Thunderstorms, elevated air quality, moderate flooding
- **High**: Severe storms, poor air quality, major flooding
- **Critical**: Tornadoes, hazardous air quality, emergency-level flooding, earthquakes

### Hazard Types
- **Weather**: Storms, tornadoes, hurricanes, extreme temperatures, hail
- **Air Quality**: Poor air quality, pollution, wildfire smoke
- **Water**: Floods, flash floods, tsunami warnings
- **Geological**: Earthquakes, landslides, seismic activity
- **Other**: Environmental emergencies, combined hazards

## Privacy & Ethics

- Focuses on public safety information
- Uses official sources and verified data
- Respects privacy and environmental regulations
- Clear data attribution and sourcing
- No sensationalism, factual reporting only

## Dependencies

See `requirements.txt` for full list:
- google-genai >= 1.0.0
- google-adk >= 0.2.0
- pydantic >= 2.4
- google-cloud-pubsub >= 2.16.0
- functions-framework
- httpx >= 0.27

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_GENAI_USE_VERTEXAI=0

# Run the agent
python __main__.py
```

### Testing

```bash
# Test with a sample query
python __main__.py "Show environmental hazards for the last 24 hours"
```

## Deployment

### Google Cloud Function

```bash
# Deploy to Google Cloud Functions
gcloud functions deploy environment-monitoring-agent \
  --runtime python311 \
  --trigger-topic environment-update-trigger \
  --entry-point runEnvironmentMonitoringAgent \
  --set-env-vars GOOGLE_API_KEY=your-key
```

## Future Enhancements

- Integration with real-time sensor networks
- Predictive hazard forecasting
- Impact zone mapping and visualization
- Multi-language alerts
- Mobile push notifications
- Historical trend analysis
- Community reporting integration

## Contributing

When contributing to the environment agent:
1. Maintain accuracy and factual reporting
2. Prioritize official/verified sources
3. Test with various locations and time ranges
4. Update documentation for new features
5. Follow the existing agent architecture patterns

## Support

For issues or questions about the Environment Monitoring Agent, please refer to the main GridWatch documentation or contact the development team.
