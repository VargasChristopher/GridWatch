from typing import List, Dict, Any
from datetime import datetime, timezone
import os

# Initialize Firestore client with error handling
db = None
INC = None

try:
    from google.cloud import firestore
    # Uses default database "(default)" in your project/region
    db = firestore.Client()
    INC = db.collection("incidents")
    print("Firestore client initialized successfully")
except Exception as e:
    print(f"Warning: Firestore not available: {e}")
    print("Running in local mode without persistence")

def upsert_incidents(items: List[Dict[str, Any]]) -> None:
    """Insert or update incidents in batch."""
    if not items:
        return
    
    if db is None or INC is None:
        print(f"Firestore not available, skipping upsert of {len(items)} incidents")
        return
    
    try:
        batch = db.batch()
        for it in items:
            it["created_at"] = it.get("created_at") or datetime.now(timezone.utc).isoformat()
            doc = INC.document(it["id"])
            batch.set(doc, it, merge=True)
        batch.commit()
        print(f"Successfully upserted {len(items)} incidents to Firestore")
    except Exception as e:
        print(f"Error upserting incidents to Firestore: {e}")

def query_incidents(limit: int = 20, since_iso: str | None = None) -> List[Dict[str, Any]]:
    """Return incidents sorted by created_at desc; optional since filter."""
    if db is None or INC is None:
        print("Firestore not available, returning empty incidents list")
        return []
    
    try:
        q = INC.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        if since_iso:
            q = q.where("created_at", ">", since_iso)
        return [d.to_dict() for d in q.stream()]
    except Exception as e:
        print(f"Error querying incidents from Firestore: {e}")
        return []