#!/bin/bash

# GridWatch Backend Startup Script
# This script starts the FastAPI backend server

echo "Starting GridWatch Backend..."

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "No .env file found. Using default values or system environment variables."
fi

# Set default values if not already set
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS:-""}
export PORT=${PORT:-"8000"}

# Activate virtual environment
cd /Users/nathanalbe/Desktop/GridWatch/backend
source .venv/bin/activate

# Start the backend server
echo "Starting FastAPI server on port $PORT..."
uvicorn main:app --reload --port $PORT
