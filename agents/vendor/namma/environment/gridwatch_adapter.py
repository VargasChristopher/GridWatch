"""
Adapter to convert environment coordinator output to GridWatch incident format.
This bridges the detailed environment agent output to the simplified GridWatch schema.
"""

import time
from typing import List, Dict, Any
from datetime import datetime


def severity_to_score(severity_text: str) -> float:
    """Convert severity text to 0.0-1.0 score."""
    severity_map = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2
    }
    return severity_map.get(severity_text.lower(), 0.5)


def source_to_confidence(source_text: str) -> float:
    """Convert source description to confidence score."""
    source_lower = source_text.lower()
    
    # Official agencies = highest confidence
    if "weather service" in source_lower or "nws" in source_lower or "noaa" in source_lower:
        return 0.95
    
    if "epa" in source_lower or "usgs" in source_lower or "geological" in source_lower:
        return 0.9
    
    # Multi-source or verified = high confidence
    if "multi-source" in source_lower or "verified" in source_lower:
        return 0.85
    
    # Official agencies = high confidence
    if "agency" in source_lower or "official" in source_lower:
        return 0.8
    
    # News sources = medium confidence
    if "news" in source_lower:
        return 0.7
    
    # Default
    return 0.6


def parse_timestamp(timestamp_str: str) -> int:
    """Convert timestamp string to unix timestamp."""
    try:
        # Try parsing various timestamp formats
        # Format: "14:30 EST" or similar
        # For now, return current time as we need more context
        return int(time.time())
    except:
        return int(time.time())


def geocode_location(location: str, city_center_lat: float, city_center_lng: float) -> tuple:
    """
    Simple geocoding fallback. In production, this should use Google Maps Geocoding API.
    For now, returns city center coordinates.
    """
    # TODO: Implement actual geocoding using Google Maps API
    # For now, return approximate coordinates based on city center
    return (city_center_lat, city_center_lng)


def convert_environment_to_incident(
    environment_entry: Dict[str, Any],
    city_center_lat: float = 38.9072,
    city_center_lng: float = -77.0369
) -> Dict[str, Any]:
    """
    Convert an environment digest entry to GridWatch incident format.
    
    Args:
        environment_entry: Dict with keys: timestamp, location, hazard_type,
                          severity, description, source, advice
        city_center_lat: Default latitude for geocoding fallback
        city_center_lng: Default longitude for geocoding fallback
    
    Returns:
        Dict in GridWatch incident format
    """
    # Extract coordinates (in production, geocode the location)
    location = environment_entry.get("location", "Unknown")
    lat, lng = geocode_location(location, city_center_lat, city_center_lng)
    
    # Convert severity text to score
    severity = severity_to_score(environment_entry.get("severity", "medium"))
    
    # Convert source to confidence
    confidence = source_to_confidence(environment_entry.get("source", ""))
    
    # Parse timestamp
    updated_at = parse_timestamp(environment_entry.get("timestamp", ""))
    
    # Build sources list
    source_text = environment_entry.get("source", "Unknown")
    sources = [s.strip() for s in source_text.split(",")]
    
    return {
        "type": "environment",
        "lat": lat,
        "lng": lng,
        "severity": severity,
        "confidence": confidence,
        "where": location,
        "etaMinutes": 0,  # Environmental hazards are current events
        "sources": sources,
        "updatedAt": updated_at
    }


def convert_environment_digest_to_incidents(
    environment_digest: List[Dict[str, Any]],
    city_center_lat: float = 38.9072,
    city_center_lng: float = -77.0369
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convert full environment digest to GridWatch incidents payload.
    
    Args:
        environment_digest: List of environment entries from environment coordinator
        city_center_lat: Default latitude for geocoding
        city_center_lng: Default longitude for geocoding
    
    Returns:
        Dict with "incidents" key containing list of GridWatch incidents
    """
    incidents = []
    
    for environment_entry in environment_digest:
        if isinstance(environment_entry, dict):
            incident = convert_environment_to_incident(
                environment_entry,
                city_center_lat,
                city_center_lng
            )
            incidents.append(incident)
    
    return {"incidents": incidents}


# Example usage
if __name__ == "__main__":
    # Example environment digest entry
    sample_environment = {
        "timestamp": "14:30 EST",
        "location": "Downtown area",
        "hazard_type": "Severe Thunderstorm",
        "severity": "High",
        "description": "Severe thunderstorm warning with large hail",
        "source": "National Weather Service",
        "advice": "Seek shelter indoors"
    }
    
    # Convert to GridWatch incident
    incident = convert_environment_to_incident(sample_environment)
    print("Converted Incident:")
    print(incident)
    
    # Convert full digest
    digest = convert_environment_digest_to_incidents([sample_environment])
    print("\nFull Payload:")
    print(digest)
