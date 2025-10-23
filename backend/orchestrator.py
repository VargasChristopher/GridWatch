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
        
        # Try to extract area information from raw data
        area_info = None
        for e in cluster:
            if hasattr(e, 'raw') and e.raw and isinstance(e.raw, dict):
                if 'area' in e.raw:
                    area_info = e.raw['area']
                    break
                elif 'city' in e.raw:
                    area_info = e.raw['city']
                    break
        
        # Create summary with area information if available
        base_summary = summary_for(inc_type, verdict)
        if area_info:
            base_summary = f"{base_summary} Location: {area_info}."
        
        inc = Incident(
            id=key,
            type=inc_type,
            lat=lat,
            lng=lng,
            confidence=verdict["confidence"],
            severity=verdict["severity"],
            summary=base_summary,
            impact=verdict["impact"],
            why=WhyCard(**verdict["why"]),
            actions=[ActionStep(**a) for a in verdict["actions"]],
            sources=[{"source_type": e.source_type, "url": e.url, "confidence": e.confidence} for e in cluster],
        )
        incidents.append(inc)

    incidents.sort(key=lambda x: x.severity, reverse=True)
    return incidents