# agents/gridwatch_agents/src/normalise.py
from typing import List, Dict, Any

def to_incidents(raw: List[Dict[str, Any]], domain: str) -> Dict[str, Any]:
    out = []
    for e in raw or []:
        out.append({
            "type": e.get("type", domain),
            "lat": float(e["lat"]),
            "lng": float(e["lng"]),
            "severity": float(e.get("severity", 0.5)),
            "confidence": float(e.get("confidence", 0.7)),
            "where": e.get("where",""),
            "etaMinutes": int(e.get("etaMinutes", 0)),
            "sources": e.get("sources", []),
            "updatedAt": int(e.get("ts") or e.get("updatedAt") or 0),
        })
    return {"incidents": out}
