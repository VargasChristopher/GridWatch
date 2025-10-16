"""
Hybrid Incident Data Aggregator
Pulls from multiple free public data sources to create realistic incidents:
- Open311 (311 service requests)
- OpenWeatherMap (weather alerts)
- USGS (earthquakes, geological events)
- OpenStreetMap (traffic/congestion patterns)
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import random
import math
from models import Evidence, EventType, SourceType

# City data with coordinates and Open311 jurisdiction IDs
CITIES = {
    "Washington, DC": {
        "lat": 38.9072,
        "lng": -77.0369,
        "open311_jurisdiction": "dc.gov",
        "state": "DC",
        "radius_m": 3000,
    },
    "New York, NY": {
        "lat": 40.7128,
        "lng": -74.0060,
        "open311_jurisdiction": "nyc.gov",
        "state": "NY",
        "radius_m": 3000,
    },
    "Los Angeles, CA": {
        "lat": 34.0522,
        "lng": -118.2437,
        "open311_jurisdiction": "lacity.gov",
        "state": "CA",
        "radius_m": 3000,
    },
    "Seattle, WA": {
        "lat": 47.6062,
        "lng": -122.3321,
        "open311_jurisdiction": "seattle.gov",
        "state": "WA",
        "radius_m": 3000,
    },
    "San Francisco, CA": {
        "lat": 37.7749,
        "lng": -122.4194,
        "open311_jurisdiction": "sfgov.org",
        "state": "CA",
        "radius_m": 3000,
    },
    "Miami, FL": {
        "lat": 25.7617,
        "lng": -80.1918,
        "open311_jurisdiction": "miamigov.com",
        "state": "FL",
        "radius_m": 3000,
    },
    "Chicago, IL": {
        "lat": 41.8781,
        "lng": -87.6298,
        "open311_jurisdiction": "chicago.gov",
        "state": "IL",
        "radius_m": 3000,
    },
    "Dallas, TX": {
        "lat": 32.7767,
        "lng": -96.7970,
        "open311_jurisdiction": "dallascityhall.com",
        "state": "TX",
        "radius_m": 3000,
    },
    "Las Vegas, NV": {
        "lat": 36.1699,
        "lng": -115.1398,
        "open311_jurisdiction": "lasvegas.gov",
        "state": "NV",
        "radius_m": 3000,
    },
    "Denver, CO": {
        "lat": 39.7392,
        "lng": -104.9903,
        "open311_jurisdiction": "denvergov.org",
        "state": "CO",
        "radius_m": 3000,
    },
}

# Event severity and probability for realistic distribution
EVENT_PROFILES = {
    "congestion": {"severity": 0.3, "probability": 0.5, "icon": "🚗"},
    "accident": {"severity": 0.6, "probability": 0.3, "icon": "🚨"},
    "road_closure": {"severity": 0.7, "probability": 0.2, "icon": "🚧"},
    "lane_restriction": {"severity": 0.4, "probability": 0.4, "icon": "🛣️"},
    "power_outage": {"severity": 0.8, "probability": 0.05, "icon": "⚡"},
    "water_main_break": {"severity": 0.7, "probability": 0.1, "icon": "💧"},
    "gas_leak": {"severity": 0.9, "probability": 0.02, "icon": "⛽"},
}


def fetch_open311_requests(city: str, city_data: Dict) -> List[Dict]:
    """
    Fetch 311 service requests from Open311 API.
    These represent citizen-reported issues like potholes, street damage, etc.
    """
    try:
        jurisdiction = city_data["open311_jurisdiction"]
        print(f"   📋 Fetching Open311 requests for {jurisdiction}...")
        
        # Most Open311 endpoints are open and don't require auth
        # Using a standard endpoint pattern
        base_url = f"https://open311.{jurisdiction}/api/v2"
        
        # Try common Open311 endpoints
        endpoints = [
            f"https://311.{jurisdiction}/api/v2/requests.json",
            f"https://api.{jurisdiction}/open311/requests.json",
            f"https://open311.{jurisdiction}/api/v2/requests.json",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    endpoint,
                    params={"status": "open", "limit": 50},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    requests_list = data if isinstance(data, list) else data.get("requests", [])
                    print(f"      ✅ Found {len(requests_list)} Open311 requests")
                    return requests_list[:20]  # Return top 20
            except:
                continue
        
        print(f"      ⚠️  Open311 endpoint not available for {jurisdiction}")
        return []
        
    except Exception as e:
        print(f"      ⚠️  Error fetching Open311: {e}")
        return []


def fetch_weather_alerts(city: str, city_data: Dict) -> List[Dict]:
    """
    Fetch weather alerts using free OpenWeatherMap API.
    Returns severe weather that could impact city infrastructure.
    """
    try:
        print(f"   🌦️  Checking weather alerts for {city}...")
        
        # Using open-meteo.com (free, no API key needed)
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": city_data["lat"],
                "longitude": city_data["lng"],
                "current": "weather_code,wind_speed",
                "daily": "weather_code,precipitation_sum,wind_speed_max",
                "timezone": "auto",
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            
            alerts = []
            
            # Check for severe weather conditions
            weather_code = current.get("weather_code", 0)
            wind_speed = current.get("wind_speed", 0)
            
            # WMO Weather Codes: 80+ = rain, 85+ = heavy rain, 70+ = snow
            if weather_code >= 80:
                alerts.append({
                    "type": "congestion",
                    "description": "Heavy rain affecting traffic",
                    "severity": 0.4 if weather_code < 85 else 0.6,
                    "source": "weather",
                })
            
            if wind_speed > 50:  # High wind
                alerts.append({
                    "type": "accident",
                    "description": "High winds reported - potential accidents",
                    "severity": 0.5,
                    "source": "weather",
                })
            
            if alerts:
                print(f"      ✅ Found {len(alerts)} weather alerts")
            
            return alerts
        
        return []
        
    except Exception as e:
        print(f"      ⚠️  Error fetching weather: {e}")
        return []


def fetch_usgs_earthquakes(city: str, city_data: Dict) -> List[Dict]:
    """
    Fetch recent earthquakes using USGS API.
    Only relevant for certain regions but adds realism.
    """
    try:
        print(f"   🌍 Checking for seismic activity near {city}...")
        
        lat = city_data["lat"]
        lng = city_data["lng"]
        
        # USGS Earthquake Hazards API (free, no key needed)
        response = requests.get(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            
            # Filter earthquakes within ~100km of city
            nearby_quakes = []
            for feature in features:
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [])
                
                if len(coords) >= 2:
                    quake_lng, quake_lat = coords[0], coords[1]
                    
                    # Calculate distance
                    dist_km = haversine(lat, lng, quake_lat, quake_lng)
                    
                    if dist_km < 100:
                        magnitude = props.get("mag", 3.0)
                        
                        if magnitude >= 4.0:  # Only significant quakes
                            nearby_quakes.append({
                                "type": "accident",  # Could cause accidents
                                "description": f"Magnitude {magnitude} earthquake detected",
                                "severity": min(0.9, 0.4 + magnitude * 0.1),
                                "source": "usgs",
                                "magnitude": magnitude,
                            })
            
            if nearby_quakes:
                print(f"      ✅ Found {len(nearby_quakes)} recent earthquakes")
            
            return nearby_quakes
        
        return []
        
    except Exception as e:
        print(f"      ⚠️  Error fetching earthquakes: {e}")
        return []


def generate_synthetic_incidents(city: str, city_data: Dict) -> List[Dict]:
    """
    Generate realistic synthetic incidents based on city characteristics.
    Used to fill gaps and ensure diverse incident types.
    """
    incidents = []
    
    print(f"   🎲 Generating synthetic incidents for {city}...")
    
    # Generate incidents based on probability profiles
    for event_type, profile in EVENT_PROFILES.items():
        if random.random() < profile["probability"]:
            # Generate 1-3 incidents of this type
            count = random.randint(1, 3)
            
            for _ in range(count):
                # Random location within city bounds (rough ~5km radius)
                lat = city_data["lat"] + random.uniform(-0.03, 0.03)
                lng = city_data["lng"] + random.uniform(-0.03, 0.03)
                
                # Random start time in last 4 hours
                hours_ago = random.randint(0, 4)
                start_time = datetime.utcnow() - timedelta(hours=hours_ago, minutes=random.randint(0, 60))
                
                incidents.append({
                    "type": event_type,
                    "lat": lat,
                    "lng": lng,
                    "start_time": start_time.isoformat() + "Z",
                    "description": f"{event_type.replace('_', ' ').title()} reported in {city}",
                    "severity": profile["severity"] + random.uniform(-0.1, 0.1),
                    "confidence": random.uniform(0.5, 0.95),
                    "source": "synthetic",
                    "source_type": "manual",
                })
    
    if incidents:
        print(f"      ✅ Generated {len(incidents)} synthetic incidents")
    
    return incidents


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in km."""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def transform_incident_to_evidence(incident: Dict, city: str) -> Optional[Evidence]:
    """Transform incident data to Evidence format."""
    try:
        # Extract and validate data
        lat = incident.get("lat")
        lng = incident.get("lng")
        event_type = incident.get("type", "congestion")
        
        if not lat or not lng:
            return None
        
        # Parse time
        start_time = incident.get("start_time")
        if start_time and isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                start_time = None
        
        # Create Evidence
        evidence = Evidence(
            evidence_id=f"{incident.get('source', 'unknown')}_{uuid.uuid4()}",
            source_type=incident.get("source_type", "manual"),  # type: ignore
            type=event_type,  # type: ignore
            lat=float(lat),
            lng=float(lng),
            radius_m=incident.get("radius_m", 200),
            start_time=start_time,
            confidence=min(0.99, max(0.5, incident.get("confidence", 0.7))),
            url=incident.get("url"),
            raw=incident,
            detected_at=datetime.utcnow()
        )
        
        return evidence
        
    except Exception as e:
        print(f"      ⚠️  Transform error: {e}")
        return None


def aggregate_incidents_for_city(city: str, city_data: Dict) -> List[Evidence]:
    """
    Aggregate incidents from all sources for a city.
    """
    print(f"\n🔗 Aggregating data for {city}...")
    
    all_incidents = []
    
    # Fetch from multiple sources
    open311_requests = fetch_open311_requests(city, city_data)
    all_incidents.extend(open311_requests)
    
    weather_alerts = fetch_weather_alerts(city, city_data)
    all_incidents.extend(weather_alerts)
    
    earthquakes = fetch_usgs_earthquakes(city, city_data)
    all_incidents.extend(earthquakes)
    
    # Always add synthetic to ensure diversity
    synthetic = generate_synthetic_incidents(city, city_data)
    all_incidents.extend(synthetic)
    
    # Transform to Evidence
    evidence_list = []
    for incident in all_incidents:
        evidence = transform_incident_to_evidence(incident, city)
        if evidence:
            evidence_list.append(evidence)
    
    print(f"   📊 Total: {len(evidence_list)} evidence items aggregated")
    
    return evidence_list


def ingest_all_cities(backend_url: str = "http://localhost:8000") -> Dict[str, int]:
    """
    Aggregate and ingest incidents for all cities.
    """
    print("\n" + "=" * 60)
    print("🌐 Hybrid Incident Data Aggregator")
    print("   Sources: Open311 + Weather + USGS + Synthetic")
    print("=" * 60)
    
    results = {}
    total_ingested = 0
    
    for city, city_data in CITIES.items():
        try:
            # Aggregate from all sources
            evidence_list = aggregate_incidents_for_city(city, city_data)
            
            if not evidence_list:
                print(f"   ℹ️  No incidents for {city}")
                results[city] = 0
                continue
            
            # Ingest into backend
            try:
                response = requests.post(
                    f"{backend_url}/evidence",
                    json=[e.model_dump(mode='json') for e in evidence_list],
                    timeout=10
                )
                response.raise_for_status()
                
                count = response.json().get("count", len(evidence_list))
                print(f"   ✅ Ingested {count} incidents into backend")
                results[city] = count
                total_ingested += count
                
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Backend error: {e}")
                results[city] = 0
        
        except Exception as e:
            print(f"   ❌ Error processing {city}: {e}")
            results[city] = 0
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Aggregation Summary")
    print("=" * 60)
    
    for city, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {city:25} {count:3} incidents")
    
    print(f"\n🎯 Total Incidents Ingested: {total_ingested}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    import sys
    
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    try:
        ingest_all_cities(backend_url)
        print("\n✅ Data aggregation complete! Test the Alexa skill now.")
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
