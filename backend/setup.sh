#!/bin/bash

# GridWatch Backend Setup Script

echo "Setting up GridWatch Backend..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To start the server:"
echo "  source .venv/bin/activate"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "To test the API:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/evidence -H 'Content-Type: application/json' --data @mocks/open311.json"
echo "  curl http://localhost:8000/incidents"
