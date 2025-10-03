#!/bin/bash

# GridWatch Complete System Startup Script
# Starts backend, agents, and frontend

echo "🚀 Starting GridWatch Complete System..."

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using default values or system environment variables."
fi

# Set default values if not already set
export GOOGLE_API_KEY=${GOOGLE_API_KEY:-"your_google_api_key_here"}
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS:-""}
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
export FRONTEND_PORT=${FRONTEND_PORT:-"3000"}
export GRIDWATCH_BBOX=${GRIDWATCH_BBOX:-"-77.044,38.895,-77.028,38.905"}
export GRIDWATCH_CITY=${GRIDWATCH_CITY:-"Washington, DC"}
export AGENT_POLL_INTERVAL=${AGENT_POLL_INTERVAL:-"60"}

echo "🔧 Configuration:"
echo "  Backend URL: $BACKEND_URL"
echo "  Frontend Port: $FRONTEND_PORT"
echo "  City: $GRIDWATCH_CITY"
echo "  BBox: $GRIDWATCH_BBOX"
echo "  Agent Poll Interval: ${AGENT_POLL_INTERVAL}s"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are available
if check_port 8000; then
    echo "❌ Port 8000 is already in use. Please stop the existing service."
    exit 1
fi

if check_port $FRONTEND_PORT; then
    echo "❌ Port $FRONTEND_PORT is already in use. Please stop the existing service."
    exit 1
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is healthy
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start agents
echo "🤖 Starting agent runner..."
./start_agents.sh &
AGENTS_PID=$!

# Wait a moment for agents to initialize
sleep 3

# Start frontend
echo "🌐 Starting frontend server..."
python3 serve_frontend.py &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo ""
echo "🎉 GridWatch System Started Successfully!"
echo ""
echo "📊 Services:"
echo "  Backend API: http://localhost:8000"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Health Check: http://localhost:8000/health"
echo "  Incidents API: http://localhost:8000/incidents"
echo ""
echo "🔄 Data Flow:"
echo "  Agents → Backend → Firestore → Frontend"
echo "  Polling every ${AGENT_POLL_INTERVAL} seconds"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down GridWatch system..."
    kill $BACKEND_PID 2>/dev/null
    kill $AGENTS_PID 2>/dev/null  
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
wait
