"""
GridWatch Web Scraper
Fetches real incident data from gridwatch.dev and ingests into local backend
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import Evidence, EventType, SourceType

# GridWatch webapp API (reverse-engineered from gridwatch.dev)
GRIDWATCH_WEB_URL = "https://gridwatch.dev"

# City coordinates for filtering
CITY_COORDS = {
    "Washington, DC": {"lat": 38.9072, "lng": -77.0369},
    "New York, NY": {"lat": 40.7128, "lng": -74.0060},
    "Los Angeles, CA": {"lat": 34.0522, "lng": -118.2437},
    "Seattle, WA": {"lat": 47.6062, "lng": -122.3321},
    "San Francisco, CA": {"lat": 37.7749, "lng": -122.4194},
    "Miami, FL": {"lat": 25.7617, "lng": -80.1918},
    "Chicago, IL": {"lat": 41.8781, "lng": -87.6298},
    "Dallas, TX": {"lat": 32.7767, "lng": -96.7970},
    "Las Vegas, NV": {"lat": 36.1699, "lng": -115.1398},
    "Denver, CO": {"lat": 39.7392, "lng": -104.9903},
}

# Event type mapping from GridWatch incident types to our EventType
INCIDENT_TYPE_MAPPING = {
    "traffic": "congestion",
    "accident": "accident",
    "congestion": "congestion",
    "road_closure": "road_closure",
    "lane_restriction": "lane_restriction",
    "power_outage": "power_outage",
    "water_main_break": "water_main_break",
    "water_line_break": "water_line_break",
    "gas_leak": "gas_leak",
    "internet_outage": "internet_outage",
}


def fetch_incidents_from_gridwatch(city: str, radius_km: float = 25) -> List[Dict]:
    """
    Fetch incidents from gridwatch.dev for a specific city.
    
    Args:
        city: City name (e.g., "Washington, DC")
        radius_km: Search radius in kilometers
        
    Returns:
        List of incident dictionaries
    """
    try:
        print(f"🔍 Fetching incidents for {city} from gridwatch.dev...")
        
        # Try to get incidents via the web API
        # GridWatch uses a query parameter approach
        params = {
            "city": city,
            "limit": 100,
        }
        
        response = requests.get(
            f"{GRIDWATCH_WEB_URL}/api/incidents",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        incidents = data.get("incidents", []) if isinstance(data, dict) else data
        print(f"   ✅ Found {len(incidents)} incidents")
        return incidents
        
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Could not fetch from API: {e}")
        print(f"   ℹ️  GridWatch may not have a public API endpoint")
        return []


def transform_incident_to_evidence(incident: Dict, city: str) -> Optional[Evidence]:
    """
    Transform a GridWatch incident to Evidence format for our backend.
    
    Args:
        incident: Raw incident from GridWatch
        city: City name for context
        
    Returns:
        Evidence object or None if transformation fails
    """
    try:
        # Extract basic info from incident
        incident_id = incident.get("id") or incident.get("incident_id") or str(uuid.uuid4())
        incident_type = incident.get("type", "congestion").lower()
        
        # Map to our EventType
        mapped_type = INCIDENT_TYPE_MAPPING.get(incident_type, "congestion")
        
        # Get coordinates
        lat = incident.get("latitude") or incident.get("lat")
        lng = incident.get("longitude") or incident.get("lng")
        
        if not lat or not lng:
            # Use city center as fallback
            city_data = CITY_COORDS.get(city)
            if not city_data:
                return None
            lat, lng = city_data["lat"], city_data["lng"]
        
        # Get time info
        start_time = incident.get("start_time")
        if start_time and isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                start_time = None
        
        # Get confidence and severity
        confidence = float(incident.get("confidence", 0.7))
        severity = float(incident.get("severity", 0.5))
        
        # Get source type
        source_type = incident.get("source_type", "manual")
        if source_type not in ["open311", "here_incident", "here_flow", "tweet", "news", "manual"]:
            source_type = "manual"
        
        # Create Evidence object
        evidence = Evidence(
            evidence_id=f"gridwatch_{incident_id}_{datetime.utcnow().isoformat()}",
            source_type=source_type,  # type: ignore
            type=mapped_type,  # type: ignore
            lat=float(lat),
            lng=float(lng),
            radius_m=incident.get("radius_m", 80),
            start_time=start_time,
            end_time=incident.get("end_time"),
            confidence=confidence,
            url=incident.get("url"),
            raw=incident,
            detected_at=datetime.utcnow()
        )
        
        return evidence
        
    except Exception as e:
        print(f"   ⚠️  Failed to transform incident: {e}")
        return None


def ingest_incidents_for_city(
    backend_url: str,
    city: str,
    radius_km: float = 25
) -> int:
    """
    Fetch incidents from gridwatch.dev and ingest into local backend.
    
    Args:
        backend_url: URL of local backend (e.g., http://localhost:8000)
        city: City to fetch incidents for
        radius_km: Search radius
        
    Returns:
        Number of incidents successfully ingested
    """
    print(f"\n📍 Ingesting incidents for {city}...")
    
    # Fetch from GridWatch
    raw_incidents = fetch_incidents_from_gridwatch(city, radius_km)
    
    if not raw_incidents:
        print(f"   ℹ️  No incidents found for {city}")
        return 0
    
    # Transform to Evidence format
    evidence_list = []
    for incident in raw_incidents:
        evidence = transform_incident_to_evidence(incident, city)
        if evidence:
            evidence_list.append(evidence)
    
    if not evidence_list:
        print(f"   ⚠️  Could not transform any incidents")
        return 0
    
    # Ingest into backend
    try:
        response = requests.post(
            f"{backend_url}/evidence",
            json=[e.model_dump(mode='json') for e in evidence_list],
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        count = result.get("count", len(evidence_list))
        print(f"   ✅ Ingested {count} incidents into backend")
        return count
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to ingest into backend: {e}")
        return 0


def ingest_all_cities(backend_url: str = "http://localhost:8000") -> Dict[str, int]:
    """
    Ingest incidents for all supported cities.
    
    Args:
        backend_url: URL of local backend
        
    Returns:
        Dictionary mapping city to incident count
    """
    print("\n🔄 GridWatch Real-Time Data Ingestion")
    print("=" * 50)
    
    results = {}
    for city in CITY_COORDS.keys():
        count = ingest_incidents_for_city(backend_url, city)
        results[city] = count
    
    print("\n" + "=" * 50)
    print("📊 Ingestion Summary:")
    total = sum(results.values())
    for city, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {city:25} {count:3} incidents")
    
    print(f"\n🎯 Total: {total} incidents ingested")
    return results


if __name__ == "__main__":
    import sys
    
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    try:
        ingest_all_cities(backend_url)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
