#!/bin/bash

# GridWatch Enhanced Agent Runner
# Runs all 5 agents (traffic, outage, crime, environment, emergency) periodically

echo "🚀 Starting GridWatch Enhanced Agent Runner"
echo "============================================="

# Check for API key (cloud backend has its own environment variables)
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️ GOOGLE_API_KEY not found in local environment"
    echo "This is normal - your cloud backend has its own API key configured"
    echo "The agents will use the cloud backend's environment variables"
fi
export BACKEND_URL="https://gridwatch-backend-554454627121.us-east1.run.app"
export AGENT_POLL_INTERVAL="300"  # 5 minutes
export GRIDWATCH_CITY="Washington, DC"
export GRIDWATCH_BBOX="-77.044,38.895,-77.028,38.905"

# Check if backend is running
echo "🔍 Checking backend health..."
if curl -s https://gridwatch-backend-554454627121.us-east1.run.app/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not accessible. Please check your connection."
    exit 1
fi

# Run the enhanced agent runner
echo "🚀 Starting all 5 agents..."
echo "   🚗 Traffic Agent"
echo "   ⚡ Energy/Outage Agent" 
echo "   🚔 Crime Agent"
echo "   🌍 Environment Agent"
echo "   🚨 Emergency Agent"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd /Users/nathanalbe/Desktop/GridWatch
python3.11 integration/enhanced_agent_runner.py
