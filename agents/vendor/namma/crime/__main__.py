"""Main entry point for running the crime agent standalone."""

if __name__ == "__main__":
    from crime_coordinator import get_crime_digest
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Provide crime and safety information for the last 24 hours"
    
    print(f"\n🚔 GridWatch Crime Monitoring Agent")
    print(f"Query: {query}\n")
    
    digest = get_crime_digest(query)
    
    print("\n=== Crime Digest ===\n")
    
    if isinstance(digest.crime_digest, list) and len(digest.crime_digest) > 0:
        for idx, incident in enumerate(digest.crime_digest, 1):
            if isinstance(incident, dict):
                print(f"{idx}. [{incident.get('severity', 'Unknown')}] {incident.get('timestamp', 'N/A')}")
                print(f"   Location: {incident.get('location', 'Unknown')}")
                print(f"   Type: {incident.get('incident_type', 'Unknown')}")
                print(f"   Description: {incident.get('description', 'No description')}")
                print(f"   Source: {incident.get('source', 'Unknown')}")
                print(f"   Advice: {incident.get('advice', 'Stay alert')}")
                print()
    else:
        print("No crime incidents found for the specified criteria.")
    
    print("\n" + "="*50 + "\n")
