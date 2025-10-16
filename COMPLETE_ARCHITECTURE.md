# GridWatch Complete Agent Architecture

## System Overview

GridWatch now has a powerful multi-agent orchestration system that monitors and aggregates incidents across four critical domains:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GridWatch Orchestrator                           │
│                     (root_agent.yaml) Sequential                         │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                    ┌─────────────────────┴──────────────────┐
                    │                                        │
        ┌───────────▼──────────┐              ┌──────────────▼───────────┐
        │  Gather Agent        │              │  Aggregator Agent        │
        │  (ParallelAgent)     │              │  (LlmAgent)              │
        └─┬──────────┬────┬────┘              └──────────┬───────────────┘
          │          │    │                             │
    ┌─────▼┐  ┌─────▼┐ ┌─┴──────┐ ┌──────────────────┐│
    │Traffic│  │Outage│ │Crime  │ │Environment     ││
    │Agent  │  │Agent │ │Agent  │ │Agent           ││
    └───┬───┘  └──┬───┘ └─┬──────┘ └────┬───────────┘│
        │         │       │             │           │
    ┌───▼─────┬───▼──┬────▼────┬─────────▼──────┐   │
    │Incident │Data  │Incident │Environmental  │   │
    │Schema   │Flow  │Schema   │Hazards         │   │
    └─────────┴──────┴─────────┴────────────────┘   │
                                                    │
                            ┌───────────────────────┘
                            │
                    ┌───────▼──────────┐
                    │ Merged Output    │
                    │ (All Incidents)  │
                    │ Deduplicated &   │
                    │ Sorted by        │
                    │ Severity         │
                    └──────────────────┘
```

---

## Agent Details

### 1️⃣ Traffic Agent
**Purpose**: Monitor transportation incidents and congestion
- BBMP civic works and alerts
- BTP traffic status
- Social media traffic reports
- Weather impact on traffic

**Output**: `type: "traffic"`
**Sources**: BBMP, BTP, social feeds, weather
**Confidence Range**: 0.5-0.9

---

### 2️⃣ Outage Agent
**Purpose**: Track power outages and utility failures
- BESCOM power outage reports
- Grid status updates
- Restoration timelines

**Output**: `type: "outage"`
**Sources**: BESCOM, news, public reports
**Confidence Range**: 0.6-1.0

---

### 3️⃣ Crime Agent
**Purpose**: Monitor public safety and crime incidents
- Official police reports
- Crime news from verified sources
- Community safety alerts

**Output**: `type: "crime"`
**Sources**: Police, news outlets, community reports
**Confidence Range**: 0.4-1.0

---

### 4️⃣ Environment Agent ✨ NEW
**Purpose**: Track environmental hazards and weather alerts
- **Weather Sub-Agent**: Severe weather, storms, extreme conditions
- **Air Quality Sub-Agent**: AQI, pollution, wildfire smoke
- **Environmental Alerts Sub-Agent**: Floods, earthquakes, hazards

**Output**: `type: "environment"`
**Sources**: NWS, EPA, USGS, NOAA, geological agencies
**Confidence Range**: 0.3-0.95

---

## Data Flow Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│ 1. USER REQUEST or PERIODIC TRIGGER                           │
│    (via API, Pub/Sub, or scheduled)                           │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ 2. GATHER PHASE (Parallel Execution)                         │
│    ✓ Traffic Agent     (queries BBMP, BTP, social)          │
│    ✓ Outage Agent      (queries BESCOM, news)               │
│    ✓ Crime Agent       (queries police, news, social)       │
│    ✓ Environment Agent (queries NWS, EPA, USGS)            │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ 3. AGGREGATION PHASE                                          │
│    • Merge 4 incident streams                                │
│    • Deduplicate (200m radius, 15 min window)               │
│    • Sort by severity (Critical → Low)                       │
│    • Validate against schema                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ 4. OUTPUT PHASE                                               │
│    {                                                          │
│      "incidents": [                                          │
│        {type, lat, lng, severity, confidence, ...},         │
│        {type, lat, lng, severity, confidence, ...},         │
│        ...                                                   │
│      ]                                                       │
│    }                                                          │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ 5. DISTRIBUTION                                              │
│    → Backend API                                            │
│    → Firestore Database                                     │
│    → Frontend Display                                       │
│    → Alert Systems                                          │
└────────────────────────────────────────────────────────────────┘
```

---

## Incident Schema (Unified)

All incidents conform to this schema:

```python
class Incident(BaseModel):
    type: Literal["traffic", "outage", "crime", "environment"]
    lat: float              # Latitude
    lng: float              # Longitude
    severity: float         # 0.0-1.0 (higher = more severe)
    confidence: float       # 0.0-1.0 (source reliability)
    where: str             # Human-readable location
    etaMinutes: int        # Estimated time until resolved
    sources: List[str]     # Data sources cited
    updatedAt: int         # Unix timestamp
```

---

## Severity Scale (Unified)

```
1.0 (Critical)    ❗❗❗ Life-threatening, emergency conditions
                  • Tornadoes, shootings, major floods
                  • Hazardous air quality, earthquakes 7+
                  
0.8 (High)        ❗❗  Significant impact, serious conditions
                  • Severe storms, violent crimes
                  • Major flooding, poor air, earthquakes 6-6.9
                  
0.5 (Medium)      ❗   Noticeable impact, some concern
                  • Thunderstorms, property crimes
                  • Moderate flooding, moderate air quality
                  
0.2 (Low)         ⚠️   Minor impact, routine information
                  • Advisories, minor incidents
                  • Minor weather, minor pollution
```

---

## Confidence Scale (By Source)

```
0.95-1.0  🏛️  Official Government Agencies
          • NWS, EPA, USGS, NOAA
          • Police departments
          • Utility companies
          
0.85-0.90 📰 Verified News Organizations
          • Major newspapers, TV stations
          • Wire services (AP, Reuters)
          • Professional journalists
          
0.70-0.80 📺 Established Media
          • Local news, local outlets
          • Community organizations
          
0.50-0.70 💬 Community Reports
          • Social media (verified)
          • Multiple corroborating sources
          
0.30-0.50 📱 Unverified Community
          • Single social media reports
          • Anecdotal reports
```

---

## Integration Points

### Backend Integration
✅ Works seamlessly with existing GridWatch backend:
- `models.py` - Schema validation
- `db_firestore.py` - Data storage
- `main.py` - API endpoints
- `orchestrator.py` - Orchestration

### Frontend Integration
✅ Display on map with type-specific colors and icons:
- Traffic: 🚗 Orange
- Outage: ⚡ Red
- Crime: 🚔 Purple
- Environment: 🌍 Blue

### External Systems
✅ Can connect to:
- Alert/notification systems
- Emergency services
- Public information systems
- Mobile apps
- Third-party platforms

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Parallel Agents | 4 (simultaneous) |
| Avg Query Time | 5-30 seconds |
| Data Sources per Agent | 1-4 |
| Incident Dedupe Radius | 200 meters |
| Dedupe Time Window | 15 minutes |
| Schema Validation | Pydantic (strict) |
| Update Frequency | On-demand or periodic |

---

## Configuration Files

```
/workspaces/GridWatch/gridwatch_config/agents/
├── root_agent.yaml          # Main orchestrator
├── gather.yaml              # Parallel executor
├── aggregator.yaml          # Merger & sorter
├── traffic_agent.yaml       # Traffic config
├── outage_agent.yaml        # Outage config
├── crime_agent.yaml         # Crime config
└── environment_agent.yaml   # Environment config ✨
```

---

## Usage Examples

### Command Line
```bash
# Test environment agent
python __main__.py "Show environmental hazards for downtown"

# Test through orchestrator
python run_orchestrator.py
```

### Python API
```python
from gridwatch_agents.src.run_orchestrator import run_orchestrator

incidents = run_orchestrator(
    city="Washington, DC",
    bbox=(-77.044, 38.895, -77.028, 38.905)
)

for incident in incidents:
    print(f"{incident['type']}: {incident['where']}")
```

### Pub/Sub Integration
```json
{
  "lat": 38.9072,
  "lon": -77.0369,
  "areas": ["Downtown", "National Park"],
  "timeframe": "last 24 hours"
}
```

---

## Complete GridWatch Capabilities

✅ **Real-Time Monitoring**
- Traffic congestion and incidents
- Power outages and utilities
- Crime and public safety
- Environmental hazards and weather

✅ **Multi-Source Intelligence**
- Official government agencies
- Verified news sources
- Community reports
- Specialized monitoring services

✅ **Intelligent Aggregation**
- Parallel data collection
- Automatic deduplication
- Severity-based sorting
- Confidence scoring

✅ **Unified Output**
- Consistent schema for all incident types
- Geographic coordinates
- Severity and confidence metrics
- Source attribution

✅ **Scalability**
- Add new agents easily
- Parallel execution
- Cloud-native architecture
- Serverless deployment ready

---

## Future Expansion

The architecture is designed to easily add new agents:

1. **Emergency Agent** (Ready to build)
   - Road closures
   - Emergency escorts
   - Public alerts

2. **Health Agent** (Example)
   - Disease outbreaks
   - Hospital status
   - Medical emergencies

3. **Utility Agent** (Example)
   - Water system status
   - Gas leaks
   - Infrastructure damage

All follow the same proven pattern! 🎯

---

**GridWatch is a comprehensive, scalable, multi-agent incident monitoring system!** 🚀
