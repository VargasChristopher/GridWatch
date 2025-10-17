from typing import List, Dict
from models import Evidence

WEIGHTS = {
    "open311": 1.0,
    "here_incident": 0.9,
    "here_flow": 0.8,
    "news": 0.7,
    "tweet": 0.5,
    "manual": 0.6,
}

def verify_and_score(inc_type: str, cluster: List[Evidence]) -> Dict:
    base = sum(e.confidence * WEIGHTS.get(e.source_type, 0.5) for e in cluster) / max(1, len(cluster))
    distinct_sources = len(set(e.source_type for e in cluster))
    bonus = min(0.15, 0.05 * (distinct_sources - 1))

    rules_fired, cross = [], []
    jf_boost, cong = 0.0, 0.0
    for e in cluster:
        if e.source_type == "here_flow":
            jf = float(e.raw.get("jamFactor", 0)) / 10.0  # 0..1
            cong = max(cong, jf)
            if jf >= 0.7 and inc_type in ("water_main_break", "road_closure"):
                jf_boost = 0.10
                rules_fired.append("traffic_corroboration")

    confidence = max(0.0, min(1.0, base + bonus + jf_boost))
    severity = 0.6 * confidence + 0.4 * cong
    impact = {"eta_delta_min": int(round(15 * cong))} if cong > 0 else None

    actions = []
    if inc_type == "water_main_break":
        actions = [
            {"step": "Notify Water Dept on-call", "owner": "Water", "priority": 1, "status": "pending"},
            {"step": "Stage cones at nearest cross-streets", "owner": "Traffic", "priority": 1, "status": "pending"},
            {"step": "Publish detour via 5th→Pine", "owner": "Traffic", "priority": 2, "status": "pending"},
        ]
    elif inc_type in ("road_closure", "lane_restriction"):
        actions = [
            {"step": "Publish closure advisory", "owner": "Traffic", "priority": 1, "status": "pending"},
            {"step": "Adjust signal timing +10s", "owner": "Traffic", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "power_outage":
        actions = [
            {"step": "Notify utility on-call", "owner": "Utility", "priority": 1, "status": "pending"},
            {"step": "Publish outage advisory", "owner": "Ops", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "internet_outage":
        actions = [
            {"step": "Contact ISP NOC", "owner": "ISP", "priority": 1, "status": "pending"},
            {"step": "Advise alternate connectivity", "owner": "Ops", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "gas_leak":
        actions = [
            {"step": "Dispatch Fire Dept", "owner": "Fire Dept", "priority": 1, "status": "pending"},
            {"step": "Notify gas utility", "owner": "Utility", "priority": 1, "status": "pending"},
        ]
    elif inc_type == "accident":
        actions = [
            {"step": "Dispatch EMS/Police", "owner": "EMS", "priority": 1, "status": "pending"},
            {"step": "Place cones / reroute", "owner": "Traffic", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "crime":
        actions = [
            {"step": "Dispatch Police", "owner": "Police", "priority": 1, "status": "pending"},
            {"step": "Secure area if needed", "owner": "Police", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "environment":
        actions = [
            {"step": "Issue public advisory", "owner": "Emergency Management", "priority": 1, "status": "pending"},
            {"step": "Monitor conditions", "owner": "Environmental", "priority": 2, "status": "pending"},
        ]
    elif inc_type == "emergency":
        actions = [
            {"step": "Activate emergency response", "owner": "Emergency Management", "priority": 1, "status": "pending"},
            {"step": "Notify relevant agencies", "owner": "Emergency Management", "priority": 1, "status": "pending"},
        ]

    return {
        "confidence": confidence,
        "severity": severity,
        "impact": impact,
        "why": {"rules_fired": rules_fired, "cross_checks": cross},
        "actions": actions,
    }

def summary_for(inc_type: str, v: Dict) -> str:
    base = {
        "water_main_break": "Likely water main break; traffic impact expected.",
        "road_closure": "Road closure reported; detours recommended.",
        "lane_restriction": "Lane restriction detected; moderate delays.",
        "congestion": "Traffic congestion detected.",
        "power_outage": "Power outage reported.",
        "water_line_break": "Water line break reported.",
        "gas_leak": "Gas leak reported.",
        "internet_outage": "Internet outage reported.",
        "accident": "Traffic accident reported.",
        "crime": "Crime incident reported.",
        "environment": "Environmental hazard detected.",
        "emergency": "Emergency alert issued."
    }.get(inc_type, "Incident detected.")
    
    # Check if impact exists and has eta_delta_min
    impact = v.get("impact")
    if impact and isinstance(impact, dict) and impact.get("eta_delta_min"):
        base += f" ETA impact ~{impact['eta_delta_min']} min."
    
    return base