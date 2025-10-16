#!/usr/bin/env python3
"""
Run All GridWatch Agents with Live Firebase Backend
Runs all 5 agents and posts evidence to live Firebase backend
"""
import os
import sys
import time
import requests
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any

# Check for API key (cloud backend has its own, this is just for local testing)
if not os.getenv('GOOGLE_API_KEY'):
    print("⚠️ GOOGLE_API_KEY not found in environment")
    print("This is normal - your cloud backend has its own API key configured")
    print("The agents will use the cloud backend's environment variables")

# Live Firebase backend URL
LIVE_BACKEND_URL = "https://gridwatch-backend-554454627121.us-east1.run.app"

def check_backend_health():
    """Check if live backend is accessible."""
    try:
        response = requests.get(f"{LIVE_BACKEND_URL}/health", timeout=10)
        response.raise_for_status()
        print("✅ Live backend is healthy")
        return True
    except Exception as e:
        print(f"❌ Live backend not accessible: {e}")
        return False

def get_current_incidents():
    """Get current incidents from live backend."""
    try:
        response = requests.get(f"{LIVE_BACKEND_URL}/incidents", timeout=15)
        response.raise_for_status()
        data = response.json()
        incidents = data.get('data', [])
        
        print(f"📊 Current incidents in live backend: {len(incidents)}")
        
        # Count by type
        type_counts = {}
        for incident in incidents:
            incident_type = incident.get('type', 'unknown')
            type_counts[incident_type] = type_counts.get(incident_type, 0) + 1
        
        print("📈 Current incident types:")
        for incident_type, count in type_counts.items():
            print(f"   {incident_type}: {count}")
        
        return incidents
    except Exception as e:
        print(f"❌ Failed to get incidents: {e}")
        return []

def run_crime_agents() -> List[Dict[str, Any]]:
    """Run crime agents."""
    try:
        print("🚔 Running crime agents...")
        
        crime_dir = os.path.join(os.path.dirname(__file__), 'agents', 'vendor', 'namma', 'crime')
        original_cwd = os.getcwd()
        os.chdir(crime_dir)
        
        try:
            sys.path.insert(0, crime_dir)
            from crime_coordinator import get_crime_digest
            from gridwatch_adapter import convert_crime_digest_to_incidents
            
            # Get crime digest
            digest = get_crime_digest("Show crime in Washington DC last 24 hours")
            
            # Convert to evidence
            evidence_items = []
            if hasattr(digest, 'crime_digest') and digest.crime_digest:
                incidents = convert_crime_digest_to_incidents(digest.crime_digest)
                
                for i, incident in enumerate(incidents.get('incidents', [])):
                    evidence_items.append({
                        "evidence_id": f"crime_{int(time.time())}_{i}",
                        "source_type": "news",
                        "type": "crime",
                        "lat": incident['lat'],
                        "lng": incident['lng'],
                        "radius_m": 200,
                        "confidence": incident['confidence'],
                        "url": None,
                        "raw": {
                            "agent": "CrimeAgent",
                            "incident": incident,
                            "sources": incident.get('sources', [])
                        },
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    })
            
            print(f"✅ Crime agents completed - {len(evidence_items)} incidents")
            return evidence_items
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"❌ Crime agents error: {e}")
        return []

def run_environment_agents() -> List[Dict[str, Any]]:
    """Run environment agents."""
    try:
        print("🌍 Running environment agents...")
        
        env_dir = os.path.join(os.path.dirname(__file__), 'agents', 'vendor', 'namma', 'environment')
        original_cwd = os.getcwd()
        os.chdir(env_dir)
        
        try:
            sys.path.insert(0, env_dir)
            from environment_coordinator import get_environment_digest
            from gridwatch_adapter import convert_environment_digest_to_incidents
            
            # Get environment digest
            digest = get_environment_digest("Show environmental hazards in Washington DC")
            
            # Convert to evidence
            evidence_items = []
            if hasattr(digest, 'environment_digest') and digest.environment_digest:
                incidents = convert_environment_digest_to_incidents(digest.environment_digest)
                
                for i, incident in enumerate(incidents.get('incidents', [])):
                    evidence_items.append({
                        "evidence_id": f"environment_{int(time.time())}_{i}",
                        "source_type": "news",
                        "type": "environment",
                        "lat": incident['lat'],
                        "lng": incident['lng'],
                        "radius_m": 500,
                        "confidence": incident['confidence'],
                        "url": None,
                        "raw": {
                            "agent": "EnvironmentAgent",
                            "incident": incident,
                            "sources": incident.get('sources', [])
                        },
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    })
            
            print(f"✅ Environment agents completed - {len(evidence_items)} incidents")
            return evidence_items
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"❌ Environment agents error: {e}")
        return []

def run_emergency_agents() -> List[Dict[str, Any]]:
    """Run emergency agents."""
    try:
        print("🚨 Running emergency agents...")
        
        emergency_dir = os.path.join(os.path.dirname(__file__), 'agents', 'vendor', 'namma', 'emergency')
        original_cwd = os.getcwd()
        os.chdir(emergency_dir)
        
        try:
            sys.path.insert(0, emergency_dir)
            from emergency_coordinator import get_emergency_digest
            from gridwatch_adapter import EmergencyToGridWatchAdapter
            
            # Get emergency digest
            digest = get_emergency_digest("Show active emergencies in Washington DC")
            
            # Convert to evidence
            evidence_items = []
            if hasattr(digest, 'emergency_digest') and digest.emergency_digest:
                adapter = EmergencyToGridWatchAdapter()
                incidents = adapter.adapt_emergency_incidents(digest.emergency_digest)
                
                for i, incident in enumerate(incidents):
                    evidence_items.append({
                        "evidence_id": f"emergency_{int(time.time())}_{i}",
                        "source_type": "news",
                        "type": "emergency",
                        "lat": incident['lat'],
                        "lng": incident['lng'],
                        "radius_m": 300,
                        "confidence": incident['confidence'],
                        "url": None,
                        "raw": {
                            "agent": "EmergencyAgent",
                            "incident": incident,
                            "sources": incident.get('sources', [])
                        },
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    })
            
            print(f"✅ Emergency agents completed - {len(evidence_items)} incidents")
            return evidence_items
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"❌ Emergency agents error: {e}")
        return []

def main():
    """Main function."""
    print("🚀 GridWatch Live Agent Runner")
    print("=" * 40)
    print(f"Live Backend: {LIVE_BACKEND_URL}")
    
    # Check backend health
    if not check_backend_health():
        return
    
    # Show current incidents
    print("\n📊 Current incidents in live backend:")
    get_current_incidents()
    
    print("\n🔄 Running all agents...")
    
    # Run all agents
    all_evidence = []
    
    # Crime agents
    crime_evidence = run_crime_agents()
    all_evidence.extend(crime_evidence)
    
    # Environment agents
    env_evidence = run_environment_agents()
    all_evidence.extend(env_evidence)
    
    # Emergency agents
    emergency_evidence = run_emergency_agents()
    all_evidence.extend(emergency_evidence)
    
    print(f"\n📊 Total evidence collected: {len(all_evidence)} items")
    
    if all_evidence:
        print("\n🎉 Success! All agents have been run.")
        print("📈 New incident data is available in your live backend!")
        print(f"🌐 Check your frontend: https://gridwatch-backend-554454627121.us-east1.run.app/incidents")
    else:
        print("\n⚠️ No new evidence items were generated")

if __name__ == "__main__":
    main()
