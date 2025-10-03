from fastapi import FastAPI, Query
from typing import List, Optional
from .models import Evidence
from .evidence_bus import EvidenceBus
from .orchestrator import build_incidents
from .transform import to_public
from .db_firestore import upsert_incidents, query_incidents

app = FastAPI(title="GridWatch Orchestrator")
bus = EvidenceBus(ttl_seconds=300)

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

    # Serve from Firestore so UI survives restarts / cold starts
    rows = query_incidents(limit=limit, since_iso=since)
    return {"data": rows}
