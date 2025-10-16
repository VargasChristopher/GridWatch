# Crime Agent Implementation Summary

## 📁 Directory Structure

```
agents/vendor/namma/crime/
├── __init__.py                          # Package initialization
├── __main__.py                          # Standalone entry point
├── crime_coordinator.py                 # Main coordinator agent
├── prompt.py                            # Coordinator prompt/instructions
├── main.py                             # Cloud Function entry point
├── pubsub.py                           # Pub/Sub integration
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Container configuration
├── README.md                           # Documentation
└── sub_agents/
    ├── __init__.py
    ├── police/
    │   ├── __init__.py
    │   ├── agent.py                    # Police reports agent
    │   └── police_prompt.py            # Police agent instructions
    ├── news/
    │   ├── __init__.py
    │   ├── agent.py                    # Crime news agent
    │   └── news_prompt.py              # News agent instructions
    └── social_media/
        ├── __init__.py
        ├── agent.py                    # Social media monitoring agent
        └── social_media_prompt.py      # Social media agent instructions
```

## 🏗️ Architecture

### Coordinator Agent
**crime_coordinator** - Orchestrates all sub-agents and produces unified crime digest

### Sub-Agents
1. **police_agent** - Official police reports and bulletins
   - Searches police department websites
   - Monitors official crime mapping services
   - Collects public safety announcements
   
2. **crime_news_agent** - Credible news sources
   - Major newspapers and TV stations
   - Wire services (AP, Reuters)
   - Professional crime beat reporting
   
3. **crime_social_agent** - Crowdsourced reports
   - Twitter/X community reports
   - Facebook neighborhood groups
   - Reddit local discussions
   - Nextdoor safety alerts

## 🔄 Data Flow

```
User Query → crime_coordinator
              ↓
    ┌─────────┴──────────┐
    ↓         ↓          ↓
police_agent  news_agent  social_agent
    ↓         ↓          ↓
    └─────────┬──────────┘
              ↓
    Cross-verify & Score
              ↓
    Format Crime Digest
              ↓
    JSON Output
```

## 📊 Output Format

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

## 🎯 Key Features

### Severity Levels
- **Critical**: Active threats, major incidents
- **High**: Violent crimes, armed robbery
- **Medium**: Property crimes, theft, burglary
- **Low**: Minor incidents, suspicious activity

### Source Credibility
- **High**: Official police/verified accounts
- **Medium**: Multiple sources, corroborated
- **Low**: Single unverified source
- **Verified**: Multi-source confirmation

### Crime Type Classification
- Violent Crimes (assault, robbery, shooting)
- Property Crimes (theft, burglary, vandalism)
- Public Safety (suspicious activity, disturbances)
- Other (fraud, drug-related, etc.)

## 🚀 Usage

### Standalone Python
```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
python -m crime "Show me crime in downtown last 24 hours"
```

### As Module
```python
from agents.vendor.namma.crime.crime_coordinator import get_crime_digest

digest = get_crime_digest("Crime reports for Capitol Hill today")
print(digest.crime_digest)
```

### Cloud Function (Pub/Sub)
```json
{
  "lat": 38.9072,
  "lon": -77.0369,
  "areas": ["Downtown", "Capitol Hill"],
  "timeframe": "last 24 hours",
  "crime_types": "all"
}
```

## 🔒 Privacy & Ethics

- No personal identification of victims/suspects
- Prioritizes official sources
- Clear credibility marking
- Focuses on public safety, not sensationalism
- Respects privacy laws and ethical standards

## 📦 Dependencies

- google-genai >= 1.0.0
- google-adk >= 0.2.0
- pydantic >= 2.4
- google-cloud-pubsub >= 2.16.0
- functions-framework
- httpx >= 0.27

## 🔧 Configuration

Environment variables needed:
- `GOOGLE_API_KEY`: Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS`: GCP service account
- `project_id`: GCP project (default: "namm-omni-dev")
- `topic_id`: Pub/Sub topic (default: "crime-update-data")

## ✅ Completed

All files have been created following the same pattern as the existing traffic and energy agents:

✓ Crime coordinator with async processing
✓ Three specialized sub-agents (police, news, social media)
✓ Comprehensive prompts with detailed instructions
✓ Pub/Sub integration for cloud deployment
✓ Docker containerization
✓ Standalone execution capability
✓ Full documentation

## 🎯 Next Steps for Environment & Emergency Agents

The same pattern can be followed for:

1. **Environment Agent** (`agents/vendor/namma/environment/`)
   - Sub-agents: weather_severe, air_quality, environmental_alerts
   - Focus: Storms, extreme weather, air quality, environmental hazards

2. **Emergency Agent** (`agents/vendor/namma/emergency/`)
   - Sub-agents: road_closures, emergency_services, public_alerts
   - Focus: Road closures, emergency escorts, public safety alerts

Both would follow the same architecture and structure as the crime agent!
