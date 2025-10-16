# Crime Monitoring Agent

## Overview

The Crime Monitoring Agent is part of the GridWatch system, designed to collect, analyze, and report crime and public safety information from multiple sources. It provides real-time crime intelligence to help residents and visitors stay informed about safety conditions in their area.

## Architecture

The agent uses a hierarchical multi-agent system:

### Coordinator
- **crime_coordinator**: Main orchestrator that aggregates data from all sub-agents and produces a unified crime digest

### Sub-Agents
1. **police_agent**: Collects official crime reports and bulletins from police departments and law enforcement agencies
2. **crime_news_agent**: Gathers crime reports from credible news sources and media outlets
3. **crime_social_agent**: Monitors social media platforms for crowdsourced crime and safety reports

## Features

- **Multi-Source Intelligence**: Aggregates data from official, news, and social media sources
- **Credibility Assessment**: Evaluates and flags the reliability of each report
- **Cross-Verification**: Identifies incidents reported by multiple sources for higher confidence
- **Severity Scoring**: Assigns severity levels (Low, Medium, High, Critical) based on incident type and verification
- **Time-Based Filtering**: Supports queries for specific time ranges (last 24 hours, today, custom ranges)
- **Location-Based**: Filters incidents by geographic area or neighborhood
- **Crime Type Classification**: Categorizes incidents (violent crimes, property crimes, public safety, etc.)

## Usage

### Direct Python Usage

```python
from crime_coordinator import get_crime_digest

# Query for crime information
prompt = "Provide crime information for downtown area in the last 24 hours"
digest = get_crime_digest(prompt)

# Access the results
for incident in digest.crime_digest:
    print(f"{incident['timestamp']} - {incident['location']}: {incident['description']}")
```

### Cloud Function (Pub/Sub)

The agent can be deployed as a Google Cloud Function triggered by Pub/Sub messages:

```json
{
  "lat": 38.9072,
  "lon": -77.0369,
  "areas": ["Downtown", "Capitol Hill"],
  "timeframe": "last 24 hours",
  "crime_types": "all"
}
```

## Output Format

The agent produces a structured JSON output:

```json
{
  "crime_digest": [
    {
      "timestamp": "14:30 EST",
      "location": "Main Street & 5th Ave",
      "incident_type": "Vehicle Theft",
      "severity": "Medium",
      "description": "Vehicle break-in reported in parking lot",
      "source": "Police-confirmed, multi-source",
      "advice": "Secure valuables and park in well-lit areas"
    }
  ]
}
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: API key for Google Gemini
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account credentials
- `project_id`: Google Cloud project ID (default: "namm-omni-dev")
- `topic_id`: Pub/Sub topic for crime updates (default: "crime-update-data")

## Data Sources

### Official Police Sources
- Police department websites and portals
- Official police social media accounts
- Crime mapping services
- Public safety bulletins

### News Sources
- Major local and national news outlets
- TV and radio news stations
- Wire services (AP, Reuters)
- Crime beat reporters

### Social Media Sources
- Twitter/X community reports
- Facebook community groups
- Reddit local subreddits
- Nextdoor neighborhood alerts

## Privacy & Ethics

- Respects individual privacy
- Does not identify individuals unless officially released by authorities
- Focuses on public safety information, not sensationalism
- Clearly marks unverified or single-source reports
- Prioritizes official and credible sources

## Dependencies

See `requirements.txt` for full list:
- google-genai >= 1.0.0
- google-adk >= 0.2.0
- pydantic >= 2.4
- google-cloud-pubsub >= 2.16.0

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Run the agent
python -m crime_coordinator
```

### Testing

```bash
# Test with a sample query
python -c "from crime_coordinator import get_crime_digest; print(get_crime_digest('Show me crime reports for downtown today'))"
```

## Deployment

### Google Cloud Function

```bash
# Deploy to Google Cloud Functions
gcloud functions deploy crime-monitoring-agent \
  --runtime python311 \
  --trigger-topic crime-update-trigger \
  --entry-point runCrimeMonitoringAgent \
  --set-env-vars GOOGLE_API_KEY=your-key
```

## Future Enhancements

- Integration with 311 systems for non-emergency reports
- Historical crime pattern analysis
- Predictive crime hotspot identification
- Integration with emergency services APIs
- Multi-language support for diverse communities
- Enhanced geospatial clustering and visualization

## Contributing

When contributing to the crime agent:
1. Maintain privacy and ethical standards
2. Verify data sources for credibility
3. Test with various geographic locations and time ranges
4. Update documentation for new features
5. Follow the existing agent architecture patterns

## Support

For issues or questions about the Crime Monitoring Agent, please refer to the main GridWatch documentation or contact the development team.
