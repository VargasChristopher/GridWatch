# agents/gridwatch_agents/src/normalise.py
from datetime import datetime

def to_incidents(raw_items, domain: str):
    out = []
    for r in raw_items:
        out.append({
            "type": r.get("type", domain),
            "lat": r["lat"], "lng": r["lng"],
            "severity": float(r.get("severity", 0.5)),
            "confidence": float(r.get("confidence", 0.7)),
            "where": r.get("where") or r.get("locality", ""),
            "etaMinutes": r.get("eta") or r.get("etaMinutes", 0),
            "sources": r.get("sources", []),
            "updatedAt": int(r.get("ts") or datetime.utcnow().timestamp()),
        })
    return {"incidents": out}
