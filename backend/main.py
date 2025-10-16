from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import Evidence
from evidence_bus import EvidenceBus
from orchestrator import build_incidents
from transform import to_public
from db_firestore import upsert_incidents, query_incidents

app = FastAPI(title="GridWatch Orchestrator")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extended TTL to 1 hour - incidents stay fresh for longer
bus = EvidenceBus(ttl_seconds=3600)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/evidence")
def ingest_evidence(items: List[Evidence]):
    # Ingest into in-memory bus for fresh fusion
    for ev in items:
        bus.add(ev)
    return {"count": len(items)}

@app.get("/incidents")
def list_incidents(
    limit: int = Query(20, ge=1, le=100),
    since: Optional[str] = Query(None, description="ISO-8601 timestamp")
):
    # Build from fresh evidence snapshot
    internals = build_incidents(bus.snapshot())[:limit]
    public = [to_public(i).model_dump() for i in internals]

    # Persist latest snapshot to Firestore (idempotent)
    upsert_incidents(public)

    # Try to serve from Firestore, fallback to fresh data if Firestore unavailable
    rows = query_incidents(limit=limit, since_iso=since)
    
    # If Firestore is not available or returns empty, serve fresh data
    if not rows:
        # Convert datetime objects to ISO strings for JSON response
        for incident in public:
            incident['created_at'] = incident['created_at'].isoformat()
            if incident.get('time'):
                incident['time'] = incident['time'].isoformat()
        rows = public[:limit]
    
    return {"data": rows}
