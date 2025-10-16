"""Main entry point for running the environment agent standalone."""

if __name__ == "__main__":
    from environment_coordinator import get_environment_digest
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Provide environmental hazard information for the last 24 hours"
    
    print(f"\n🌍 GridWatch Environmental Monitoring Agent")
    print(f"Query: {query}\n")
    
    digest = get_environment_digest(query)
    
    print("\n=== Environmental Digest ===\n")
    
    if isinstance(digest.environment_digest, list) and len(digest.environment_digest) > 0:
        for idx, hazard in enumerate(digest.environment_digest, 1):
            if isinstance(hazard, dict):
                print(f"{idx}. [{hazard.get('severity', 'Unknown')}] {hazard.get('timestamp', 'N/A')}")
                print(f"   Location: {hazard.get('location', 'Unknown')}")
                print(f"   Type: {hazard.get('hazard_type', 'Unknown')}")
                print(f"   Description: {hazard.get('description', 'No description')}")
                print(f"   Source: {hazard.get('source', 'Unknown')}")
                print(f"   Advice: {hazard.get('advice', 'Stay informed')}")
                print()
    else:
        print("No environmental hazards found for the specified criteria.")
    
    print("\n" + "="*50 + "\n")
