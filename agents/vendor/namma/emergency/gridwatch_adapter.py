# ---------- gridwatch_adapter.py ----------
"""
GridWatch Adapter for Emergency Agent.

Converts emergency incidents to GridWatch unified incident schema.
Handles severity scoring, confidence weighting, and schema validation.
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmergencyToGridWatchAdapter:
    """
    Adapts emergency agent output to GridWatch unified incident schema.
    
    GridWatch Schema:
    {
        "type": "emergency",  # New incident type
        "severity": 0.0-1.0,   # Severity score
        "confidence": 0.0-1.0, # Confidence in data
        "lat": float,
        "lng": float,
        "where": str,          # Location description
        "etaMinutes": int,     # Estimated time to resolution
        "sources": [str],      # Data sources
        "updatedAt": str,      # ISO 8601 timestamp
    }
    """
    
    # Severity mapping for emergency types
    SEVERITY_MAPPING = {
        "evacuation": 1.0,
        "shelter_in_place": 0.9,
        "emergency_declaration": 0.85,
        "hazmat": 0.9,
        "active_emergency": 0.8,
        "fire": 0.9,
        "medical": 0.7,
        "police": 0.6,
        "road_closure": 0.7,
        "full_closure": 0.8,
        "lane_closure": 0.5,
        "amber_alert": 0.95,
        "silver_alert": 0.9,
        "public_alert": 0.7,
    }
    
    @staticmethod
    def adapt_emergency_incidents(emergency_digest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert emergency digest to GridWatch incidents.
        
        Args:
            emergency_digest: Raw emergency digest output
            
        Returns:
            List of GridWatch-formatted incident dictionaries
        """
        incidents = []
        
        emergency_list = emergency_digest.get("emergency_digest", [])
        if isinstance(emergency_list, str):
            try:
                emergency_list = eval(emergency_list)
            except:
                return []
        
        if not isinstance(emergency_list, list):
            return []
        
        for item in emergency_list:
            try:
                incident = EmergencyToGridWatchAdapter._convert_single_incident(item)
                if incident:
                    incidents.append(incident)
            except Exception as e:
                logger.error(f"Error converting incident: {str(e)}")
                continue
        
        return incidents
    
    @staticmethod
    def _convert_single_incident(item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single emergency incident to GridWatch format."""
        
        # Extract basic fields
        incident_type = item.get("type", "emergency")
        description = item.get("description", "")
        location = item.get("location", "Unknown")
        source = item.get("source", "Unknown")
        
        # Extract coordinates
        lat = item.get("lat")
        lng = item.get("lng")
        
        if lat is None or lng is None:
            logger.warning(f"Incident missing coordinates: {location}")
            return None
        
        # Map severity
        severity = float(item.get("severity", 0.5))
        severity = max(0.0, min(1.0, severity))  # Clamp 0-1
        
        # Map confidence
        confidence = float(item.get("confidence", 0.7))
        confidence = max(0.0, min(1.0, confidence))  # Clamp 0-1
        
        # Extract ETA
        eta_minutes = item.get("estimated_duration_minutes")
        if eta_minutes:
            eta_minutes = int(eta_minutes)
        
        # Build GridWatch incident
        gridwatch_incident = {
            "type": "emergency",  # Unified type
            "severity": severity,
            "confidence": confidence,
            "lat": lat,
            "lng": lng,
            "where": location,
            "etaMinutes": eta_minutes,
            "sources": [source],
            "updatedAt": item.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            "description": description,
            "emergency_type": incident_type,  # Original emergency type
        }
        
        return gridwatch_incident
    
    @staticmethod
    def score_confidence_by_source(source: str) -> float:
        """Score confidence based on data source."""
        source_lower = source.lower()
        
        if any(x in source_lower for x in ["911", "dispatch", "official", "alert system", "fema"]):
            return 0.95
        elif any(x in source_lower for x in ["police", "fire", "emergency", "dot", "agency"]):
            return 0.9
        elif any(x in source_lower for x in ["news", "alert"]):
            return 0.75
        elif any(x in source_lower for x in ["traffic", "waze", "google"]):
            return 0.65
        else:
            return 0.5
