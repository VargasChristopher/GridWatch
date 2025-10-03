from typing import List
from models import Incident
from models_public import IncidentOut, PublicSource, PublicAction

# Map internal incident.type -> external label (adjust as needed)
_TYPE_MAP = {
    "water_main_break": "water_line_break",
    # keep others as-is unless you want different labels
}

def to_public(inc: Incident) -> IncidentOut:
    external_type = _TYPE_MAP.get(inc.type, inc.type)
    sources: List[PublicSource] = [
        PublicSource(type=s.get("source_type","unknown"), confidence=float(s.get("confidence",0.0)))
        for s in inc.sources
    ]
    actions: List[PublicAction] = [
        PublicAction(step=a.step, owner=a.owner, status=a.status)
        for a in inc.actions
    ]
    return IncidentOut(
        id=inc.id,
        type=external_type,
        status=inc.status,
        lat=inc.lat,
        lng=inc.lng,
        severity=inc.severity,
        confidence=inc.confidence,
        summary=inc.summary,
        sources=sources,
        actions=actions,
        created_at=inc.created_at,
        time=inc.created_at,  # or last-updated timestamp if you track it
    )