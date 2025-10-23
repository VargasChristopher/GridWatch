#!/usr/bin/env python3
"""
Generate realistic demo incidents for all 10 GridWatch cities.
Creates diverse incident types with realistic locations and details.
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
import random
import math

# City data with coordinates
CITIES = {
    "Washington, DC": {
        "lat": 38.9072,
        "lng": -77.0369,
        "state": "DC",
        "landmarks": ["National Mall", "Capitol Hill", "Dupont Circle", "Georgetown", "Adams Morgan"]
    },
    "New York, NY": {
        "lat": 40.7128,
        "lng": -74.0060,
        "state": "NY", 
        "landmarks": ["Times Square", "Central Park", "Brooklyn Bridge", "Wall Street", "SoHo"]
    },
    "Los Angeles, CA": {
        "lat": 34.0522,
        "lng": -118.2437,
        "state": "CA",
        "landmarks": ["Hollywood", "Beverly Hills", "Santa Monica", "Downtown LA", "Venice Beach"]
    },
    "Seattle, WA": {
        "lat": 47.6062,
        "lng": -122.3321,
        "state": "WA",
        "landmarks": ["Pike Place Market", "Space Needle", "Capitol Hill", "Fremont", "Ballard"]
    },
    "San Francisco, CA": {
        "lat": 37.7749,
        "lng": -122.4194,
        "state": "CA",
        "landmarks": ["Golden Gate Bridge", "Fisherman's Wharf", "Mission District", "Castro", "SOMA"]
    },
    "Miami, FL": {
        "lat": 25.7617,
        "lng": -80.1918,
        "state": "FL",
        "landmarks": ["South Beach", "Wynwood", "Brickell", "Little Havana", "Coconut Grove"]
    },
    "Chicago, IL": {
        "lat": 41.8781,
        "lng": -87.6298,
        "state": "IL",
        "landmarks": ["Millennium Park", "Navy Pier", "Wrigleyville", "Lincoln Park", "The Loop"]
    },
    "Dallas, TX": {
        "lat": 32.7767,
        "lng": -96.7970,
        "state": "TX",
        "landmarks": ["Deep Ellum", "Uptown", "Bishop Arts", "White Rock Lake", "Downtown"]
    },
    "Las Vegas, NV": {
        "lat": 36.1699,
        "lng": -115.1398,
        "state": "NV",
        "landmarks": ["The Strip", "Fremont Street", "Summerlin", "Henderson", "Downtown"]
    },
    "Denver, CO": {
        "lat": 39.7392,
        "lng": -104.9903,
        "state": "CO",
        "landmarks": ["LoDo", "RiNo", "Capitol Hill", "Cherry Creek", "Highlands"]
    }
}

# Incident templates with realistic scenarios (using valid EventType values)
INCIDENT_TEMPLATES = {
    "congestion": [
        {
            "title": "Rush hour congestion on {highway}",
            "description": "Heavy traffic due to construction work, delays expected",
            "severity": 0.4,
            "eta": "1h",
            "highways": ["I-95", "I-66", "I-395", "US-50", "Route 1"]
        },
        {
            "title": "Traffic backup on {highway}",
            "description": "Slow moving traffic due to volume, expect delays",
            "severity": 0.3,
            "eta": "45m",
            "highways": ["I-95", "I-66", "I-395", "US-50", "Route 1"]
        }
    ],
    "accident": [
        {
            "title": "Multi-vehicle accident on {highway}",
            "description": "Multi-vehicle collision blocking {lanes} lanes, emergency services responding",
            "severity": 0.8,
            "eta": "2h",
            "highways": ["I-95", "I-66", "I-395", "US-50", "Route 1"]
        },
        {
            "title": "Vehicle collision in {area}",
            "description": "Two-vehicle accident blocking intersection, police on scene",
            "severity": 0.7,
            "eta": "1h"
        }
    ],
    "power_outage": [
        {
            "title": "Power outage affecting {area}",
            "description": "Electrical outage due to equipment failure, crews dispatched",
            "severity": 0.7,
            "eta": "3h"
        },
        {
            "title": "Electrical service interruption",
            "description": "Power lines down due to weather, restoration in progress",
            "severity": 0.8,
            "eta": "4h"
        }
    ],
    "water_main_break": [
        {
            "title": "Water main break in {area}",
            "description": "Water main break causing low pressure and street flooding",
            "severity": 0.8,
            "eta": "2h"
        },
        {
            "title": "Water service interruption",
            "description": "Water main break affecting service in {area}",
            "severity": 0.7,
            "eta": "3h"
        }
    ],
    "road_closure": [
        {
            "title": "Road closure due to utility work",
            "description": "Street closed for water main repair, detour in place",
            "severity": 0.6,
            "eta": "4h",
            "highways": ["Main St", "Broadway", "First Ave", "Second St", "Park Ave"]
        },
        {
            "title": "Construction zone closure",
            "description": "Road closed for construction work, use alternate route",
            "severity": 0.5,
            "eta": "6h",
            "highways": ["Main St", "Broadway", "First Ave", "Second St", "Park Ave"]
        }
    ]
}

def generate_city_incidents(city_name: str, city_data: Dict) -> List[Dict]:
    """Generate realistic incidents for a specific city."""
    incidents = []
    
    # Generate 3-7 incidents per city
    num_incidents = random.randint(3, 7)
    
    # Get incident types with realistic distribution (using valid EventType values)
    incident_types = ["congestion", "accident", "power_outage", "water_main_break", "road_closure"]
    type_weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Traffic most common
    
    for _ in range(num_incidents):
        # Select incident type based on weights
        incident_type = random.choices(incident_types, weights=type_weights)[0]
        
        # Get random template for this type
        template = random.choice(INCIDENT_TEMPLATES[incident_type])
        
        # Generate random location within city bounds
        lat_offset = random.uniform(-0.02, 0.02)  # ~2km radius
        lng_offset = random.uniform(-0.02, 0.02)
        lat = city_data["lat"] + lat_offset
        lng = city_data["lng"] + lng_offset
        
        # Select random landmark/area
        area = random.choice(city_data["landmarks"])
        
        # Format title and description
        title = template["title"].format(
            highway=random.choice(template.get("highways", ["Main St"])),
            area=area,
            lanes=random.choice(["2", "3", "4"])
        )
        description = template["description"].format(
            area=area,
            lanes=random.choice(["2", "3", "4"])
        )
        
        # Add some randomness to severity
        severity = template["severity"] + random.uniform(-0.1, 0.1)
        severity = max(0.1, min(1.0, severity))
        
        # Generate incident in Evidence format
        start_time = datetime.utcnow() - timedelta(hours=random.randint(0, 6))
        detected_at = datetime.utcnow()
        
        incident = {
            "evidence_id": f"demo_{city_name.replace(' ', '_').replace(',', '')}_{uuid.uuid4().hex[:8]}",
            "source_type": "manual",
            "type": incident_type,
            "lat": lat,
            "lng": lng,
            "radius_m": random.randint(100, 500),
            "start_time": start_time.isoformat() + "Z",
            "confidence": random.uniform(0.7, 0.95),
            "url": None,
            "raw": {
                "title": title,
                "description": description,
                "severity": severity,
                "eta": template["eta"],
                "area": area,
                "city": city_name,
                "source": "demo_data"
            },
            "detected_at": detected_at.isoformat() + "Z"
        }
        
        incidents.append(incident)
    
    return incidents

def post_incidents_to_backend(incidents: List[Dict], backend_url: str) -> bool:
    """Post incidents to the backend API."""
    try:
        response = requests.post(
            f"{backend_url}/evidence",
            json=incidents,
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error posting to backend: {e}")
        return False

def main():
    """Generate and post incidents for all cities."""
    backend_url = "https://gridwatch-backend-554454627121.us-east1.run.app"
    
    print("🌐 GridWatch Demo Incident Generator")
    print("=" * 50)
    
    total_incidents = 0
    
    for city_name, city_data in CITIES.items():
        print(f"\n📍 Generating incidents for {city_name}...")
        
        # Generate incidents for this city
        incidents = generate_city_incidents(city_name, city_data)
        
        if incidents:
            print(f"   ✅ Generated {len(incidents)} incidents")
            
            # Post to backend
            if post_incidents_to_backend(incidents, backend_url):
                print(f"   ✅ Posted to backend successfully")
                total_incidents += len(incidents)
            else:
                print(f"   ❌ Failed to post to backend")
        else:
            print(f"   ⚠️  No incidents generated")
    
    print(f"\n🎯 Total incidents generated: {total_incidents}")
    print("=" * 50)
    
    # Test the API to verify incidents are available
    try:
        response = requests.get(f"{backend_url}/incidents?limit=50", timeout=10)
        if response.ok:
            data = response.json()
            incident_count = len(data.get("data", []))
            print(f"✅ Backend API responding with {incident_count} total incidents")
        else:
            print("❌ Backend API not responding properly")
    except Exception as e:
        print(f"❌ Error testing backend API: {e}")

if __name__ == "__main__":
    main()
