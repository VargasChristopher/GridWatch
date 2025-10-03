from typing import List, Dict
from models import Evidence, Incident, ActionStep, WhyCard
from rules import verify_and_score, summary_for

def _cluster_key(e: Evidence) -> str:
    # coarse grid-based key to cluster nearby evidence of the same type
    return f"{e.type}:{round(e.lat,3)},{round(e.lng,3)}"

def build_incidents(evidence: List[Evidence]) -> List[Incident]:
    buckets: Dict[str, List[Evidence]] = {}
    for e in evidence:
        buckets.setdefault(_cluster_key(e), []).append(e)

    incidents: List[Incident] = []
    for key, cluster in buckets.items():
        inc_type = cluster[0].type
        lat = sum(e.lat for e in cluster) / len(cluster)
        lng = sum(e.lng for e in cluster) / len(cluster)

        verdict = verify_and_score(inc_type, cluster)
        inc = Incident(
            id=key,
            type=inc_type,
            lat=lat,
            lng=lng,
            confidence=verdict["confidence"],
            severity=verdict["severity"],
            summary=summary_for(inc_type, verdict),
            impact=verdict["impact"],
            why=WhyCard(**verdict["why"]),
            actions=[ActionStep(**a) for a in verdict["actions"]],
            sources=[{"source_type": e.source_type, "url": e.url, "confidence": e.confidence} for e in cluster],
        )
        incidents.append(inc)

    incidents.sort(key=lambda x: x.severity, reverse=True)
    return incidents