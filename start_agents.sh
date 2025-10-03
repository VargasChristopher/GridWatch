#!/bin/bash

# GridWatch Agent Runner Startup Script
# This script starts the continuous agent runner that polls for new data

echo "Starting GridWatch Agent Runner..."

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "No .env file found. Using default values or system environment variables."
fi

# Set default values if not already set
export GOOGLE_API_KEY=${GOOGLE_API_KEY:-"your_google_api_key_here"}
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS:-""}
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
export GRIDWATCH_BBOX=${GRIDWATCH_BBOX:-"-77.044,38.895,-77.028,38.905"}
export GRIDWATCH_CITY=${GRIDWATCH_CITY:-"Washington, DC"}
export AGENT_POLL_INTERVAL=${AGENT_POLL_INTERVAL:-"60"}

# Activate virtual environment
cd /Users/nathanalbe/Desktop/GridWatch/backend
source .venv/bin/activate

# Start the agent runner
cd /Users/nathanalbe/Desktop/GridWatch
python integration/agent_runner.py
