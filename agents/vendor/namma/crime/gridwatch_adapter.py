"""
Adapter to convert crime coordinator output to GridWatch incident format.
This bridges the detailed crime agent output to the simplified GridWatch schema.
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
    
    # Police-confirmed or multi-source = highest confidence
    if "police-confirmed" in source_lower or "multi-source" in source_lower:
        return 0.9
    
    # Official police = high confidence
    if "police" in source_lower and "dept" in source_lower:
        return 0.85
    
    # Verified news = medium-high confidence
    if "news" in source_lower or "verified" in source_lower:
        return 0.7
    
    # Social media = lower confidence
    if "social" in source_lower:
        return 0.5
    
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


def convert_crime_to_incident(
    crime_entry: Dict[str, Any],
    city_center_lat: float = 38.9072,
    city_center_lng: float = -77.0369
) -> Dict[str, Any]:
    """
    Convert a crime digest entry to GridWatch incident format.
    
    Args:
        crime_entry: Dict with keys: timestamp, location, incident_type, 
                     severity, description, source, advice
        city_center_lat: Default latitude for geocoding fallback
        city_center_lng: Default longitude for geocoding fallback
    
    Returns:
        Dict in GridWatch incident format
    """
    # Extract coordinates (in production, geocode the location)
    location = crime_entry.get("location", "Unknown")
    lat, lng = geocode_location(location, city_center_lat, city_center_lng)
    
    # Convert severity text to score
    severity = severity_to_score(crime_entry.get("severity", "medium"))
    
    # Convert source to confidence
    confidence = source_to_confidence(crime_entry.get("source", ""))
    
    # Parse timestamp
    updated_at = parse_timestamp(crime_entry.get("timestamp", ""))
    
    # Build sources list
    source_text = crime_entry.get("source", "Unknown")
    sources = [s.strip() for s in source_text.split(",")]
    
    return {
        "type": "crime",
        "lat": lat,
        "lng": lng,
        "severity": severity,
        "confidence": confidence,
        "where": location,
        "etaMinutes": 0,  # Crime incidents are current events
        "sources": sources,
        "updatedAt": updated_at
    }


def convert_crime_digest_to_incidents(
    crime_digest: List[Dict[str, Any]],
    city_center_lat: float = 38.9072,
    city_center_lng: float = -77.0369
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convert full crime digest to GridWatch incidents payload.
    
    Args:
        crime_digest: List of crime entries from crime coordinator
        city_center_lat: Default latitude for geocoding
        city_center_lng: Default longitude for geocoding
    
    Returns:
        Dict with "incidents" key containing list of GridWatch incidents
    """
    incidents = []
    
    for crime_entry in crime_digest:
        if isinstance(crime_entry, dict):
            incident = convert_crime_to_incident(
                crime_entry,
                city_center_lat,
                city_center_lng
            )
            incidents.append(incident)
    
    return {"incidents": incidents}


# Example usage
if __name__ == "__main__":
    # Example crime digest entry
    sample_crime = {
        "timestamp": "14:30 EST",
        "location": "Main Street & 5th Ave",
        "incident_type": "Vehicle Theft",
        "severity": "Medium",
        "description": "Vehicle break-in reported in parking lot",
        "source": "Police-confirmed, multi-source",
        "advice": "Secure valuables and park in well-lit areas"
    }
    
    # Convert to GridWatch incident
    incident = convert_crime_to_incident(sample_crime)
    print("Converted Incident:")
    print(incident)
    
    # Convert full digest
    digest = convert_crime_digest_to_incidents([sample_crime])
    print("\nFull Payload:")
    print(digest)
