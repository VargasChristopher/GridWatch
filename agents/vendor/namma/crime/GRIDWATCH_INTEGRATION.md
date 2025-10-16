# GridWatch Crime Agent Integration Guide

## Overview

The crime agent has been integrated into the GridWatch orchestrator system following your existing patterns for traffic and outage agents.

## 🔧 Configuration Files Updated

### 1. `/workspaces/GridWatch/gridwatch_config/schemas.py`
✅ Added `"crime"` to the incident type literal
```python
type: Literal["traffic", "outage", "crime"]
```

### 2. `/workspaces/GridWatch/gridwatch_config/agents/crime_agent.yaml`
✅ Created new agent configuration matching traffic/outage pattern
- Uses `gemini-2.5-flash` model
- Returns `crime_incidents` output key
- Follows same JSON schema as other agents

### 3. `/workspaces/GridWatch/gridwatch_config/agents/gather.yaml`
✅ Added crime_agent to parallel execution
```yaml
sub_agents:
  - config_path: traffic_agent.yaml
  - config_path: outage_agent.yaml
  - config_path: crime_agent.yaml  # NEW
```

### 4. `/workspaces/GridWatch/gridwatch_config/agents/aggregator.yaml`
✅ Updated to merge crime incidents with traffic and outage
```yaml
traffic={traffic_incidents}
outage={outage_incidents}
crime={crime_incidents}  # NEW
```

## 📊 Data Flow

```
User Request
    ↓
gridwatch_orchestrator (root_agent.yaml)
    ↓
gather (ParallelAgent)
    ├─→ traffic_agent.yaml
    ├─→ outage_agent.yaml
    └─→ crime_agent.yaml ← NEW
    ↓
aggregator (LlmAgent)
    ↓
Merged & Deduplicated Incidents
```

## 🎯 Output Format

Crime incidents follow the same schema as traffic/outage:

```json
{
  "incidents": [
    {
      "type": "crime",
      "lat": 38.9072,
      "lng": -77.0369,
      "severity": 0.8,
      "confidence": 0.9,
      "where": "Main St & 5th Ave",
      "etaMinutes": 0,
      "sources": ["DC Police Dept", "Local News 7"],
      "updatedAt": 1697472000
    }
  ]
}
```

## 🚀 Quick Start

### 1. Set Environment Variables

Copy the example environment file:
```bash
cp /workspaces/GridWatch/gridwatch_config/agents/.env /workspaces/GridWatch/agents/vendor/namma/crime/.env
```

Update with your API key:
```bash
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=<YOUR_API_KEY>
```

### 2. Test Crime Agent Directly

```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
export GOOGLE_API_KEY="your-key-here"
python -m crime "Show crime in Washington DC last 24 hours"
```

### 3. Test Through GridWatch Orchestrator

```bash
cd /workspaces/GridWatch/gridwatch_agents/src
python run_orchestrator.py
```

The orchestrator will now automatically:
1. Run traffic, outage, AND crime agents in parallel
2. Aggregate all incidents
3. Deduplicate within 200m and 15 minutes
4. Sort by severity

## 📝 Crime Agent Features

### Severity Mapping
- **Critical (1.0)**: Active threats, major violent incidents
- **High (0.8)**: Violent crimes, armed robbery
- **Medium (0.5)**: Property crimes, theft, burglary
- **Low (0.2)**: Suspicious activity, minor incidents

### Confidence Scoring
- **0.9-1.0**: Official police sources, multi-source verified
- **0.7-0.8**: Verified news sources
- **0.5-0.6**: Social media reports
- **0.4**: Single unverified sources

### Data Sources
1. **Official Police**: Department websites, bulletins, crime maps
2. **News Sources**: Major outlets, wire services
3. **Social Media**: Twitter, Facebook, Reddit (lower confidence)

## 🔄 Integration with Existing System

### Backend Integration (`/workspaces/GridWatch/backend/`)

The crime incidents will automatically flow through your existing backend:

1. **models.py** - Already supports any incident type
2. **db_firestore.py** - No changes needed (stores all incident types)
3. **main.py** - API endpoints work with all incident types
4. **transform.py** - Handles incident normalization

### Frontend Integration (`/workspaces/GridWatch/frontend/`)

Update your frontend to display crime incidents:

```javascript
// In webapp/js/api.js or similar
function getIncidentIcon(incident) {
  switch(incident.type) {
    case 'traffic': return '🚗';
    case 'outage': return '⚡';
    case 'crime': return '🚔';  // NEW
    default: return '⚠️';
  }
}

function getIncidentColor(incident) {
  switch(incident.type) {
    case 'traffic': return '#FF9800';
    case 'outage': return '#F44336';
    case 'crime': return '#9C27B0';  // NEW - Purple for crime
    default: return '#757575';
  }
}
```

## 🧪 Testing Checklist

- [ ] Environment variables set (GOOGLE_API_KEY)
- [ ] Crime agent runs standalone
- [ ] Crime agent runs through orchestrator
- [ ] Crime incidents appear in aggregated output
- [ ] Deduplication works across all incident types
- [ ] Frontend displays crime incidents correctly
- [ ] Pub/Sub integration (if using Cloud Functions)

## 🔧 Advanced Configuration

### Custom Geocoding

Edit `/workspaces/GridWatch/agents/vendor/namma/crime/gridwatch_adapter.py`:

```python
def geocode_location(location: str, city_center_lat: float, city_center_lng: float) -> tuple:
    """Use Google Maps Geocoding API for precise coordinates."""
    import googlemaps
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    result = gmaps.geocode(location)
    if result:
        loc = result[0]['geometry']['location']
        return (loc['lat'], loc['lng'])
    return (city_center_lat, city_center_lng)
```

### Custom Time Windows

Modify `crime_agent.yaml` to adjust lookback period:
```yaml
instruction: |
  # Change "last 24 hours" to "last 48 hours" or other timeframe
  Only include incidents from the last 24 hours
```

### Filtering by Crime Type

Add crime type filters to your queries:
```python
query = "Show only violent crimes in downtown area"
# or
query = "Property crime reports in northwest quadrant"
```

## 📊 Monitoring & Logging

Crime agent logs follow the same pattern as traffic/outage:

```bash
# View logs
tail -f /var/log/gridwatch/crime_agent.log

# Monitor Pub/Sub
gcloud pubsub subscriptions pull trigger-crime-update-agent-sub --auto-ack
```

## 🚨 Troubleshooting

### No crime incidents returned
- Check GOOGLE_API_KEY is set correctly
- Verify the search query includes location/time
- Try broadening the time window (48 hours instead of 24)

### Low confidence scores
- Crime incidents from social media have lower confidence by design
- Official sources may be limited for some areas
- Consider adjusting CRIME_SOURCE_SOCIAL_WEIGHT in config

### Duplicate incidents
- Aggregator deduplicates within 200m and 15 minutes
- Adjust thresholds in aggregator.yaml if needed

## 📈 Next Steps

1. **Deploy to production**: Use the provided Dockerfile
2. **Set up monitoring**: Configure alerts for high-severity crimes
3. **Enhance geocoding**: Integrate Google Maps API
4. **Add filtering**: UI controls for crime type filters
5. **Historical analysis**: Track crime patterns over time

## 🔐 Privacy & Security

- Crime data is aggregated from public sources only
- No personal information is stored or displayed
- Follows GDPR and privacy best practices
- Configurable data retention policies

## 📚 Related Files

- Agent Config: `/workspaces/GridWatch/gridwatch_config/agents/crime_agent.yaml`
- Schema: `/workspaces/GridWatch/gridwatch_config/schemas.py`
- Crime Coordinator: `/workspaces/GridWatch/agents/vendor/namma/crime/crime_coordinator.py`
- Adapter: `/workspaces/GridWatch/agents/vendor/namma/crime/gridwatch_adapter.py`
- Documentation: `/workspaces/GridWatch/agents/vendor/namma/crime/README.md`

---

**The crime agent is now fully integrated into GridWatch and ready to use!** 🎉
