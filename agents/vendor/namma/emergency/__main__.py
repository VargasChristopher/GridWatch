# ---------- __main__.py ----------
"""
Emergency Agent - Standalone execution.

Run with: python __main__.py "Your query here"
Example: python __main__.py "Show active emergencies in Washington DC"
"""

import sys
import json
from datetime import datetime
from emergency_coordinator import get_emergency_digest

def format_incident(incident: dict, index: int) -> str:
    """Format an emergency incident for display."""
    lines = []
    
    incident_type = incident.get("emergency_type", incident.get("type", "Emergency"))
    severity = incident.get("severity", 0.5)
    confidence = incident.get("confidence", 0.7)
    location = incident.get("location", "Unknown")
    description = incident.get("description", "")
    source = incident.get("source", "Unknown")
    updated = incident.get("updated_at", "")
    
    # Severity indicator
    if severity >= 0.9:
        severity_emoji = "🔴"
    elif severity >= 0.7:
        severity_emoji = "🟠"
    elif severity >= 0.5:
        severity_emoji = "🟡"
    else:
        severity_emoji = "🟢"
    
    lines.append(f"\n  {severity_emoji} [{index}] {incident_type.upper()}")
    lines.append(f"      Location: {location}")
    lines.append(f"      Severity: {severity:.1%} | Confidence: {confidence:.1%}")
    lines.append(f"      Description: {description}")
    lines.append(f"      Source: {source}")
    if updated:
        lines.append(f"      Updated: {updated}")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        query = "Show active emergencies"
    else:
        query = " ".join(sys.argv[1:])
    
    print("\n🚨 GridWatch Emergency Monitoring Agent")
    print("=" * 70)
    print(f"Query: {query}\n")
    
    try:
        result = get_emergency_digest(query)
        
        emergency_list = result.emergency_digest
        if isinstance(emergency_list, str):
            try:
                emergency_list = json.loads(emergency_list)
            except:
                emergency_list = []
        
        if not isinstance(emergency_list, list):
            emergency_list = []
        
        if emergency_list:
            print(f"📍 Found {len(emergency_list)} emergency incident(s):\n")
            for idx, incident in enumerate(emergency_list, 1):
                print(format_incident(incident, idx))
        else:
            print("✅ No active emergencies found.")
        
        print("\n" + "=" * 70)
        print("Response Type: emergency_digest")
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        sys.exit(1)

if __name__ == "__main__":
    main()
