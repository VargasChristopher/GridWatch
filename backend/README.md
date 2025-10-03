# GridWatch Backend

The GridWatch backend orchestrator that processes evidence from various sources and generates actionable incidents.

## Features

- **Evidence Processing**: Ingests evidence from multiple sources (Open311, HERE Traffic, etc.)
- **Intelligent Clustering**: Groups nearby evidence of the same type into incidents
- **Scoring & Verification**: Applies confidence and severity scoring with traffic corroboration
- **Action Generation**: Creates type-specific action playbooks for each incident
- **REST API**: FastAPI-based endpoints for evidence ingestion and incident retrieval
- **Firestore Integration**: Optional persistence layer for incident storage

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

For local development without Firestore:
```bash
# No additional setup needed - system runs in local mode
```

For production with Firestore:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
export HERE_API_KEY=your_here_api_key
export OPEN311_BASE=https://api.open311.org/v2
```

### 3. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Post evidence
curl -X POST http://localhost:8000/evidence \
  -H "Content-Type: application/json" \
  --data @mocks/open311.json

# Get incidents
curl http://localhost:8000/incidents
```

## API Endpoints

### POST /evidence
Ingest evidence from external sources.

**Request Body**: Array of Evidence objects
```json
[
  {
    "evidence_id": "open311_001",
    "source_type": "open311",
    "type": "water_main_break",
    "lat": 38.9012,
    "lng": -77.0365,
    "confidence": 0.88,
    "raw": {...}
  }
]
```

**Response**: `{"count": 3}`

### GET /incidents
Retrieve processed incidents.

**Query Parameters**:
- `limit` (optional): Number of incidents to return (default: 20)
- `since` (optional): ISO-8601 timestamp filter

**Response**: 
```json
{
  "data": [
    {
      "id": "water_line_break:38.901,-77.036",
      "type": "water_line_break",
      "status": "active",
      "lat": 38.9012,
      "lng": -77.0365,
      "severity": 0.86,
      "confidence": 0.81,
      "summary": "Likely water main break; traffic impact expected. ETA impact ~12 min.",
      "sources": [{"type": "open311", "confidence": 0.88}],
      "actions": [{"step": "Notify Water Dept on-call", "owner": "Water", "status": "pending"}],
      "created_at": "2025-01-01T09:30:00Z"
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response**: `{"ok": true}`

## Architecture

```
Evidence Sources → /evidence API → EvidenceBus → Orchestrator → /incidents API
                                                      ↓
                                                Firestore (optional)
```

### Components

- **EvidenceBus**: In-memory TTL queue for fresh evidence
- **Orchestrator**: Clusters evidence and generates incidents
- **Rules Engine**: Applies scoring and verification logic
- **Transform**: Converts internal incidents to public API format
- **Firestore**: Optional persistence layer

## Evidence Types

- `water_main_break` / `water_line_break`
- `road_closure` / `lane_restriction`
- `congestion`
- `power_outage`
- `gas_leak`
- `internet_outage`
- `accident`

## Source Types

- `open311`: Open311 service requests (weight: 1.0)
- `here_incident`: HERE traffic incidents (weight: 0.9)
- `here_flow`: HERE traffic flow data (weight: 0.8)
- `news`: News reports (weight: 0.7)
- `tweet`: Social media (weight: 0.5)
- `manual`: Manual reports (weight: 0.6)

## Scoring Logic

**Confidence**:
- Base: Average of (evidence_confidence × source_weight)
- Multi-source bonus: +0.05 per additional source (max +0.15)
- Traffic corroboration: +0.10 if HERE flow jamFactor ≥ 7

**Severity**:
- 60% confidence + 40% congestion score
- Congestion score = max(jamFactor) / 10

## Development

The system is designed to work with or without Firestore. When Firestore credentials are not available, it runs in local mode and serves fresh incidents directly from the EvidenceBus.

## Mock Data

Sample evidence files are provided in `mocks/`:
- `open311.json`: Sample Open311 service requests
- `here_flow.json`: Sample HERE traffic data

Use these for testing and demos.
