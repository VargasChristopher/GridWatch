from google.cloud import firestore
from typing import List, Dict, Any
from datetime import datetime, timezone

# Uses default database "(default)" in your project/region
db = firestore.Client()
INC = db.collection("incidents")

def upsert_incidents(items: List[Dict[str, Any]]) -> None:
    """Insert or update incidents in batch."""
    if not items:
        return
    batch = db.batch()
    for it in items:
        it["created_at"] = it.get("created_at") or datetime.now(timezone.utc).isoformat()
        doc = INC.document(it["id"])
        batch.set(doc, it, merge=True)
    batch.commit()

def query_incidents(limit: int = 20, since_iso: str | None = None) -> List[Dict[str, Any]]:
    """Return incidents sorted by created_at desc; optional since filter."""
    q = INC.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
    if since_iso:
        q = q.where("created_at", ">", since_iso)
    return [d.to_dict() for d in q.stream()]