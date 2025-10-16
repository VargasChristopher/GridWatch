# Crime Agent Setup Checklist

## ✅ Completed Items

### Core Implementation
- [x] Created crime agent directory structure
- [x] Implemented crime_coordinator.py with async processing
- [x] Created comprehensive prompt.py with AI instructions
- [x] Built three sub-agents (police, news, social_media)
- [x] Added Pub/Sub integration (pubsub.py)
- [x] Created Cloud Function entry point (main.py)
- [x] Added standalone execution (__main__.py)
- [x] Created Dockerfile for containerization
- [x] Wrote comprehensive README.md

### GridWatch Integration
- [x] Updated schemas.py to include "crime" type
- [x] Created crime_agent.yaml configuration
- [x] Updated gather.yaml for parallel execution
- [x] Updated aggregator.yaml to merge crime data
- [x] Created gridwatch_adapter.py for schema conversion
- [x] Created integration test suite
- [x] Created .env.example configuration template

### Documentation
- [x] Implementation summary
- [x] Integration guide
- [x] API documentation
- [x] Setup instructions
- [x] Testing guide
- [x] Complete checklist

## 📋 Setup Tasks (For You)

### 1. Install Dependencies
```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Option A: Copy existing config
cp /workspaces/GridWatch/gridwatch_config/agents/.env \
   /workspaces/GridWatch/agents/vendor/namma/crime/.env

# Option B: Set manually
export GOOGLE_API_KEY="your-api-key-here"
export GOOGLE_GENAI_USE_VERTEXAI=0
```

### 3. Test Crime Agent Standalone
```bash
cd /workspaces/GridWatch/agents/vendor/namma/crime
python -m crime "Show crime reports for Washington DC last 24 hours"
```

Expected output: JSON with crime incidents

### 4. Test GridWatch Integration
```bash
cd /workspaces/GridWatch/gridwatch_agents/src
python run_orchestrator.py
```

Expected: Crime incidents merged with traffic and outage data

### 5. Update Frontend (Optional)
Add to your JavaScript:
```javascript
// In webapp/js/api.js or similar
function getIncidentIcon(incident) {
  const icons = {
    'traffic': '🚗',
    'outage': '⚡',
    'crime': '🚔'  // ADD THIS
  };
  return icons[incident.type] || '⚠️';
}

function getIncidentColor(incident) {
  const colors = {
    'traffic': '#FF9800',  // Orange
    'outage': '#F44336',   // Red
    'crime': '#9C27B0'     // Purple - ADD THIS
  };
  return colors[incident.type] || '#757575';
}
```

### 6. Deploy to Production (Optional)
```bash
# Build Docker image
cd /workspaces/GridWatch/agents/vendor/namma/crime
docker build -t gridwatch-crime-agent .

# Deploy to Cloud Functions (if using GCP)
gcloud functions deploy crime-monitoring-agent \
  --runtime python311 \
  --trigger-topic crime-update-trigger \
  --entry-point runCrimeMonitoringAgent \
  --set-env-vars GOOGLE_API_KEY=your-key
```

## 🧪 Verification Checklist

### Basic Functionality
- [ ] Crime agent imports successfully
- [ ] Adapter converts crime data to GridWatch format
- [ ] Configuration files exist and are valid
- [ ] Environment variables are set correctly

### Integration Tests
- [ ] Crime agent runs standalone
- [ ] Crime agent runs through orchestrator
- [ ] Crime incidents appear in aggregated output
- [ ] Deduplication works across all incident types
- [ ] Severity and confidence scores are correct

### Data Quality
- [ ] Crime incidents have valid coordinates
- [ ] Severity scores range from 0.0-1.0
- [ ] Confidence scores reflect source reliability
- [ ] Sources are properly attributed
- [ ] Timestamps are current

### Production Readiness
- [ ] Logging is working correctly
- [ ] Error handling is in place
- [ ] Rate limiting is configured
- [ ] Privacy guidelines are followed
- [ ] Performance is acceptable

## 🎯 Success Criteria

Your crime agent integration is successful when:

1. ✅ The orchestrator runs without errors
2. ✅ Crime incidents appear in the output JSON
3. ✅ Incidents have proper type="crime"
4. ✅ Severity and confidence scores are appropriate
5. ✅ Multiple data sources are being queried
6. ✅ Deduplication works correctly
7. ✅ Frontend displays crime incidents (if updated)

## 🔍 Troubleshooting

### No crime incidents returned
- Check that GOOGLE_API_KEY is set correctly
- Verify the search queries include location
- Try broadening the time window (48 hours)
- Check if Google Search tool is working

### Import errors
```bash
pip install -r requirements.txt
```

### Configuration errors
```bash
# Verify config files
ls -la /workspaces/GridWatch/gridwatch_config/agents/
cat /workspaces/GridWatch/gridwatch_config/agents/crime_agent.yaml
```

### Low data quality
- Adjust confidence thresholds in .env
- Modify search prompts in sub-agent prompts
- Enable/disable specific sub-agents

## 📊 Monitoring

After deployment, monitor:

1. **Incident Volume**: Are crime incidents being detected?
2. **Source Distribution**: Mix of police/news/social sources?
3. **Confidence Scores**: Mostly high-confidence sources?
4. **Response Times**: Sub-agent query duration?
5. **Error Rates**: Any recurring failures?

## 📚 Reference Documentation

- Main README: `/workspaces/GridWatch/agents/vendor/namma/crime/README.md`
- Integration Guide: `/workspaces/GridWatch/agents/vendor/namma/crime/GRIDWATCH_INTEGRATION.md`
- Implementation Summary: `/workspaces/GridWatch/agents/vendor/namma/crime/IMPLEMENTATION_SUMMARY.md`
- Complete Summary: `/workspaces/GridWatch/CRIME_AGENT_COMPLETE.md`

## 🚀 Next Steps

Once crime agent is working:

1. **Create Environment Agent**
   - Weather alerts, storms, air quality
   - Sub-agents: weather_severe, air_quality, environmental_alerts
   
2. **Create Emergency Agent**
   - Road closures, emergency escorts, public alerts
   - Sub-agents: road_closures, emergency_services, public_alerts

Both follow the exact same pattern as the crime agent!

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the error logs
3. Verify all configuration files
4. Test each sub-agent individually
5. Check Google API quotas and limits

---

**You're ready to use the crime agent in GridWatch!** 🎉
