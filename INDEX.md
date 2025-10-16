# GridWatch Complete System Index

## 📚 Quick Navigation

### Main Documentation
- **[COMPLETE_ARCHITECTURE.md](COMPLETE_ARCHITECTURE.md)** - Full system architecture & data flow
- **[CRIME_AGENT_COMPLETE.md](CRIME_AGENT_COMPLETE.md)** - Crime agent implementation
- **[ENVIRONMENT_AGENT_COMPLETE.md](ENVIRONMENT_AGENT_COMPLETE.md)** - Environment agent implementation

---

## 🚔 Crime Agent

**Location**: `/workspaces/GridWatch/agents/vendor/namma/crime/`

### Key Files
- `crime_coordinator.py` - Main orchestrator
- `prompt.py` - AI instructions
- `main.py` - Cloud Function entry
- `gridwatch_adapter.py` - Schema converter
- `__main__.py` - Standalone runner

### Sub-Agents
- `sub_agents/police/` - Official police reports
- `sub_agents/news/` - Crime news sources
- `sub_agents/social_media/` - Community reports

### Documentation
- `README.md` - Feature overview
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `GRIDWATCH_INTEGRATION.md` - Integration guide
- `SETUP_CHECKLIST.md` - Setup instructions

### Configuration
- `/gridwatch_config/agents/crime_agent.yaml` - Agent config

### To Test
```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
export GOOGLE_API_KEY="your-key"
pip install -r requirements.txt
python __main__.py "Show crime in Washington DC last 24 hours"
```

---

## 🌍 Environment Agent

**Location**: `/workspaces/GridWatch/agents/vendor/namma/environment/`

### Key Files
- `environment_coordinator.py` - Main orchestrator
- `prompt.py` - AI instructions
- `main.py` - Cloud Function entry
- `gridwatch_adapter.py` - Schema converter
- `__main__.py` - Standalone runner

### Sub-Agents
- `sub_agents/weather/` - Severe weather alerts
- `sub_agents/air_quality/` - Air quality monitoring
- `sub_agents/environmental_alerts/` - Environmental hazards

### Documentation
- `README.md` - Feature overview

### Configuration
- `/gridwatch_config/agents/environment_agent.yaml` - Agent config

### To Test
```bash
cd /workspaces/GridWatch/agents/vendor/namma/environment
export GOOGLE_API_KEY="your-key"
pip install -r requirements.txt
python __main__.py "Show environmental hazards"
```

---

## ⚙️ GridWatch Configuration

**Location**: `/workspaces/GridWatch/gridwatch_config/agents/`

### Configuration Files
- `root_agent.yaml` - Main orchestrator
- `gather.yaml` - Parallel agent executor
- `aggregator.yaml` - Incident merger
- `traffic_agent.yaml` - Traffic config
- `outage_agent.yaml` - Outage config
- `crime_agent.yaml` - Crime config ✨ NEW
- `environment_agent.yaml` - Environment config ✨ NEW

### Schema Files
- `schemas.py` - Incident schema (updated to include crime & environment)

---

## 🎯 System Architecture

### Data Flow
```
User Request
    ↓
Root Agent (Sequential)
    ├─→ Gather Agent (Parallel)
    │   ├─→ Traffic Agent
    │   ├─→ Outage Agent
    │   ├─→ Crime Agent ✨
    │   └─→ Environment Agent ✨
    │   ↓
    └─→ Aggregator Agent
        ↓
Merged, Deduplicated, Sorted Output
```

### Incident Types Supported
1. **traffic** - Congestion, accidents, civic works
2. **outage** - Power outages, utility failures
3. **crime** ✨ - Police reports, public safety
4. **environment** ✨ - Weather, air quality, hazards

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total New Agents | 2 (Crime, Environment) |
| Total Sub-Agents | 6 (3 per agent) |
| Total Files Created | 40+ |
| Total Lines of Code | 4,000+ |
| Configuration Files Updated | 4 |
| Data Sources | 10+ |
| Supported Incident Types | 4 |

---

## ✨ Features

### Crime Agent Monitors
- Official police reports
- Crime news from verified sources
- Community safety alerts
- Multi-source incidents

### Environment Agent Monitors
- **Weather**: Storms, tornadoes, extreme conditions
- **Air Quality**: AQI, pollution, wildfire smoke
- **Environmental Alerts**: Floods, earthquakes, hazards

### System Features
✅ Parallel execution (4 agents simultaneously)
✅ Automatic deduplication (200m radius, 15 min window)
✅ Severity-based sorting (Critical → Low)
✅ Confidence scoring (0.0-1.0)
✅ Multi-source verification
✅ Cloud-native architecture
✅ Containerized deployment ready
✅ Comprehensive logging
✅ Error handling
✅ Type safety with Pydantic

---

## 🚀 Quick Start Guide

### 1. Test Crime Agent
```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
pip install -r requirements.txt
export GOOGLE_API_KEY="your-api-key"
python __main__.py "Show crime in Washington DC"
```

### 2. Test Environment Agent
```bash
cd /workspaces/GridWatch/agents/vendor/namma/environment
pip install -r requirements.txt
export GOOGLE_API_KEY="your-api-key"
python __main__.py "Show environmental hazards"
```

### 3. Test Through Orchestrator
```bash
cd /workspaces/GridWatch/gridwatch_agents/src
python run_orchestrator.py
```

All 4 incident types (traffic, outage, crime, environment) will flow automatically!

---

## 📝 Configuration

### Environment Variables
```bash
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_GENAI_USE_VERTEXAI=0
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### Model Selection
- Crime Agent: `gemini-2.5-pro` (or `gemini-2.5-flash` for cost)
- Environment Agent: `gemini-2.5-pro` (or `gemini-2.5-flash` for cost)
- Aggregator: `gemini-2.5-flash` (configured in YAML)

---

## 🔄 Integration Points

### Backend Integration
✅ Works with existing GridWatch backend
- `models.py` - Schema validation
- `db_firestore.py` - Data storage
- `main.py` - API endpoints

### Frontend Integration
- Display crimes with 🚔 icon (purple color)
- Display environmental hazards with 🌍 icon (blue color)
- Existing traffic and outage displays unchanged

### External Systems
- Can trigger alerts and notifications
- Can integrate with emergency services
- Can feed to mobile apps
- Can integrate with third-party platforms

---

## 🎨 Severity Scale

```
1.0 - Critical     ❗❗❗ Life-threatening situations
0.8 - High         ❗❗  Significant impact
0.5 - Medium       ❗   Noticeable impact
0.2 - Low          ⚠️   Minor impact
```

---

## 🔐 Data Sources

### Crime Agent Sources
- **Police** (0.9-1.0): Official police departments
- **News** (0.7-0.8): Verified news organizations
- **Social** (0.4-0.6): Community reports

### Environment Agent Sources
- **Official** (0.95-1.0): NWS, EPA, USGS, NOAA
- **News** (0.7-0.8): Established media
- **Community** (0.3-0.6): Verified reports

---

## 📚 Additional Documentation

### Crime Agent
- [IMPLEMENTATION_SUMMARY.md](agents/vendor/namma/crime/IMPLEMENTATION_SUMMARY.md)
- [GRIDWATCH_INTEGRATION.md](agents/vendor/namma/crime/GRIDWATCH_INTEGRATION.md)
- [SETUP_CHECKLIST.md](agents/vendor/namma/crime/SETUP_CHECKLIST.md)
- [README.md](agents/vendor/namma/crime/README.md)

### Environment Agent
- [README.md](agents/vendor/namma/environment/README.md)

### System
- [COMPLETE_ARCHITECTURE.md](COMPLETE_ARCHITECTURE.md)

---

## 🚀 What's Next?

### Ready to Build
- **Emergency Agent** - Road closures, escorts, alerts
  - Same proven pattern
  - Ready to implement whenever you need it

### Future Possibilities
- Health Agent - Disease outbreaks, hospitals
- Utility Agent - Water systems, gas, infrastructure
- Commercial Agent - Business continuity alerts
- Custom Agents - Add any data source!

---

## 🆘 Troubleshooting

### API Key Error
```
ValueError: Missing key inputs argument!
```
→ Set `export GOOGLE_API_KEY="your-key"`

### 503 Service Unavailable
```
google.genai.errors.ServerError: 503 UNAVAILABLE
```
→ Google API temporarily overloaded, try again in a few minutes

### Import Errors
→ Install dependencies: `pip install -r requirements.txt`

### Configuration Not Found
→ Check file paths match `/workspaces/GridWatch/gridwatch_config/agents/`

---

## 📞 Support

For detailed information:
1. Check the relevant README.md files
2. Review COMPLETE_ARCHITECTURE.md for system design
3. Check GRIDWATCH_INTEGRATION.md for integration details
4. Review SETUP_CHECKLIST.md for configuration help

---

## 🎉 Summary

**GridWatch now has a powerful 4-agent incident monitoring system:**

| Agent | Type | Status |
|-------|------|--------|
| Traffic | Congestion & accidents | ✓ Existing |
| Outage | Power & utilities | ✓ Existing |
| Crime | Public safety | ✨ NEW |
| Environment | Weather & hazards | ✨ NEW |

**All running in parallel with automatic deduplication and severity sorting!**

Ready to deploy or extend further? 🚀
