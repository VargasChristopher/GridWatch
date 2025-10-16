#!/usr/bin/env python3
"""
Test script to verify crime agent integration with GridWatch.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    try:
        from crime_coordinator import get_crime_digest, CrimeDigestOutput
        print("✅ Crime coordinator imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_gridwatch_adapter():
    """Test the GridWatch adapter functions."""
    print("\n🧪 Testing GridWatch adapter...")
    try:
        from gridwatch_adapter import (
            convert_crime_to_incident,
            convert_crime_digest_to_incidents,
            severity_to_score,
            source_to_confidence
        )
        
        # Test severity conversion
        assert severity_to_score("critical") == 1.0
        assert severity_to_score("high") == 0.8
        assert severity_to_score("medium") == 0.5
        assert severity_to_score("low") == 0.2
        print("✅ Severity conversion works")
        
        # Test confidence conversion
        assert source_to_confidence("Police-confirmed") >= 0.85
        assert source_to_confidence("Local News 7") >= 0.65
        assert source_to_confidence("Social media") >= 0.4
        print("✅ Confidence conversion works")
        
        # Test crime to incident conversion
        sample_crime = {
            "timestamp": "14:30 EST",
            "location": "Main Street & 5th Ave",
            "incident_type": "Vehicle Theft",
            "severity": "Medium",
            "description": "Vehicle break-in reported",
            "source": "Police-confirmed",
            "advice": "Secure valuables"
        }
        
        incident = convert_crime_to_incident(sample_crime)
        assert incident["type"] == "crime"
        assert incident["severity"] == 0.5
        assert incident["confidence"] >= 0.85
        assert "Police-confirmed" in incident["sources"]
        print("✅ Crime to incident conversion works")
        
        # Test full digest conversion
        digest_payload = convert_crime_digest_to_incidents([sample_crime])
        assert "incidents" in digest_payload
        assert len(digest_payload["incidents"]) == 1
        print("✅ Full digest conversion works")
        
        return True
    except Exception as e:
        print(f"❌ Adapter test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test that crime incidents match GridWatch schema."""
    print("\n🧪 Testing schema validation...")
    try:
        # Import GridWatch schemas
        gridwatch_config_path = Path(__file__).parent.parent.parent.parent.parent / "gridwatch_config"
        sys.path.insert(0, str(gridwatch_config_path))
        
        from schemas import Incident, IncidentsPayload
        
        # Create a sample crime incident
        sample_incident = Incident(
            type="crime",
            lat=38.9072,
            lng=-77.0369,
            severity=0.8,
            confidence=0.9,
            where="Main St & 5th Ave",
            etaMinutes=0,
            sources=["DC Police Dept", "Local News"],
            updatedAt=1697472000
        )
        
        print(f"✅ Crime incident validates against schema: {sample_incident.type}")
        
        # Test full payload
        payload = IncidentsPayload(incidents=[sample_incident])
        print(f"✅ Incidents payload validates with {len(payload.incidents)} incident(s)")
        
        return True
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_files():
    """Test that configuration files exist and are valid."""
    print("\n🧪 Testing configuration files...")
    
    config_dir = Path(__file__).parent.parent.parent.parent.parent / "gridwatch_config" / "agents"
    
    files_to_check = [
        "crime_agent.yaml",
        "gather.yaml",
        "aggregator.yaml"
    ]
    
    all_exist = True
    for filename in files_to_check:
        filepath = config_dir / filename
        if filepath.exists():
            print(f"✅ {filename} exists")
            # Try to read it
            try:
                content = filepath.read_text()
                if "crime" in content.lower():
                    print(f"   ✓ Contains crime-related configuration")
            except Exception as e:
                print(f"   ⚠️  Error reading file: {e}")
        else:
            print(f"❌ {filename} missing")
            all_exist = False
    
    return all_exist

def test_environment():
    """Test environment configuration."""
    print("\n🧪 Testing environment...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "<API_KEY>":
        print("✅ GOOGLE_API_KEY is set")
    else:
        print("⚠️  GOOGLE_API_KEY not set (required for live testing)")
    
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0")
    print(f"✅ GOOGLE_GENAI_USE_VERTEXAI={use_vertex}")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("GridWatch Crime Agent Integration Tests")
    print("=" * 60)
    
    results = {
        "imports": test_imports(),
        "adapter": test_gridwatch_adapter(),
        "schema": test_schema_validation(),
        "config": test_config_files(),
        "environment": test_environment()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.capitalize():.<30} {status}")
    
    print("=" * 60)
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Crime agent is ready for integration.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
