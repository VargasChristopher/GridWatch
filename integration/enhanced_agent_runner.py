#!/usr/bin/env python3
"""
Enhanced Agent Runner for GridWatch
Continuously runs all 5 agents (traffic, outage, crime, environment, emergency) and posts evidence to the backend.
"""
import os
import time
import asyncio
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any
import sys

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models import Evidence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAgentRunner:
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or os.getenv('BACKEND_URL', 'https://gridwatch-backend-554454627121.us-east1.run.app')
        self.poll_interval = int(os.getenv('AGENT_POLL_INTERVAL', '300'))  # 5 minutes default
        self.bbox = os.getenv('GRIDWATCH_BBOX', '-77.044,38.895,-77.028,38.905')
        self.city = os.getenv('GRIDWATCH_CITY', 'Washington, DC')
        
    def run_traffic_agents(self) -> List[Dict[str, Any]]:
        """Run traffic orchestrator and return evidence."""
        try:
            logger.info("🚗 Running traffic agents...")
            
            # Change to traffic directory to find agent_config.json
            traffic_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'vendor', 'namma', 'traffic')
            original_cwd = os.getcwd()
            os.chdir(traffic_dir)
            
            try:
                # Add traffic directory to Python path
                sys.path.insert(0, traffic_dir)
                # Dynamic import to avoid path issues
                import orca
                asyncio.run(orca.call_traffic_update_agent_async("Traffic update alert: road block detected."))
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
            # The traffic orchestrator already posts to backend, so we return empty
            # If you want to capture the evidence here instead, we'd need to modify orca.py
            return []
            
        except Exception as e:
            logger.error(f"Error running traffic agents: {e}")
            return []
    
    def run_energy_agents(self) -> List[Dict[str, Any]]:
        """Run energy management agent and return evidence."""
        try:
            logger.info("⚡ Running energy agents...")
            
            # Skip energy agents if no Google Cloud credentials
            if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.info("Skipping energy agents - no Google Cloud credentials found")
                return []
            
            # Change to energy directory for proper imports
            energy_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'vendor', 'namma', 'energy')
            original_cwd = os.getcwd()
            os.chdir(energy_dir)
            
            try:
                # Add energy directory to Python path
                sys.path.insert(0, energy_dir)
                # Dynamic import to avoid path issues
                from energy_coordinator import get_energy_digest
                
                # Parse bbox for energy agent
                bbox_parts = self.bbox.split(',')
                if len(bbox_parts) == 4:
                    min_lng, min_lat, max_lng, max_lat = map(float, bbox_parts)
                    lat = (min_lat + max_lat) / 2.0
                    lng = (min_lng + max_lng) / 2.0
                else:
                    lat, lng = 38.9000, -77.0365
                
                # Create energy digest
                prompt = f"My location is {lat}, {lng}. Provide power-outage information for the next 24 hours in {self.city} including official utility notices and reliable local news reports."
                digest = get_energy_digest(prompt)
                
                # Convert to evidence
                evidence_items = []
                if hasattr(digest, 'outage_summary') and digest.outage_summary:
                    for i, outage in enumerate(digest.outage_summary):
                        evidence_items.append({
                            "evidence_id": f"energy_outage_{int(time.time())}_{i}",
                            "source_type": "news",
                            "type": "power_outage",
                            "lat": float(lat),
                            "lng": float(lng),
                            "radius_m": 200,
                            "confidence": 0.8,
                            "url": None,
                            "raw": {"agent": "EnergyAgent", "outage": outage},
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                        })
                
                return evidence_items
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
        except Exception as e:
            logger.error(f"Error running energy agents: {e}")
            return []
    
    def run_crime_agents(self) -> List[Dict[str, Any]]:
        """Run crime agents and return evidence."""
        try:
            logger.info("🚔 Running crime agents...")
            
            # Change to crime directory
            crime_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'vendor', 'namma', 'crime')
            original_cwd = os.getcwd()
            os.chdir(crime_dir)
            
            try:
                # Add crime directory to Python path
                sys.path.insert(0, crime_dir)
                from crime_coordinator import get_crime_digest
                from gridwatch_adapter import convert_crime_digest_to_incidents
                
                # Get crime digest
                prompt = f"Show crime in {self.city} last 24 hours"
                digest = get_crime_digest(prompt)
                
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
                
                return evidence_items
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.error(f"Error running crime agents: {e}")
            return []
    
    def run_environment_agents(self) -> List[Dict[str, Any]]:
        """Run environment agents and return evidence."""
        try:
            logger.info("🌍 Running environment agents...")
            
            # Change to environment directory
            env_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'vendor', 'namma', 'environment')
            original_cwd = os.getcwd()
            os.chdir(env_dir)
            
            try:
                # Add environment directory to Python path
                sys.path.insert(0, env_dir)
                from environment_coordinator import get_environment_digest
                from gridwatch_adapter import convert_environment_digest_to_incidents
                
                # Get environment digest
                prompt = f"Show environmental hazards in {self.city}"
                digest = get_environment_digest(prompt)
                
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
                
                return evidence_items
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.error(f"Error running environment agents: {e}")
            return []
    
    def run_emergency_agents(self) -> List[Dict[str, Any]]:
        """Run emergency agents and return evidence."""
        try:
            logger.info("🚨 Running emergency agents...")
            
            # Change to emergency directory
            emergency_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'vendor', 'namma', 'emergency')
            original_cwd = os.getcwd()
            os.chdir(emergency_dir)
            
            try:
                # Add emergency directory to Python path
                sys.path.insert(0, emergency_dir)
                from emergency_coordinator import get_emergency_digest
                from gridwatch_adapter import EmergencyToGridWatchAdapter
                
                # Get emergency digest
                prompt = f"Show active emergencies in {self.city}"
                digest = get_emergency_digest(prompt)
                
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
                
                return evidence_items
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.error(f"Error running emergency agents: {e}")
            return []
    
    def post_evidence(self, evidence_items: List[Dict[str, Any]]) -> bool:
        """Post evidence to backend."""
        if not evidence_items:
            return True
            
        try:
            response = requests.post(f"{self.backend_url}/evidence", json=evidence_items, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Posted {len(evidence_items)} evidence items to backend")
            return True
        except Exception as e:
            logger.error(f"❌ Error posting evidence to backend: {e}")
            return False
    
    def run_all_agents(self) -> Dict[str, int]:
        """Run all 5 agents and return counts."""
        results = {
            "traffic": 0, 
            "energy": 0, 
            "crime": 0, 
            "environment": 0, 
            "emergency": 0, 
            "errors": 0
        }
        
        # Run traffic agents (they post directly to backend)
        try:
            self.run_traffic_agents()
            results["traffic"] = 3  # Traffic orchestrator posts 3 items
        except Exception as e:
            logger.error(f"Traffic agents error: {e}")
            results["errors"] += 1
        
        # Run energy agents
        try:
            energy_evidence = self.run_energy_agents()
            if self.post_evidence(energy_evidence):
                results["energy"] = len(energy_evidence)
        except Exception as e:
            logger.error(f"Energy agents error: {e}")
            results["errors"] += 1
        
        # Run crime agents
        try:
            crime_evidence = self.run_crime_agents()
            if self.post_evidence(crime_evidence):
                results["crime"] = len(crime_evidence)
        except Exception as e:
            logger.error(f"Crime agents error: {e}")
            results["errors"] += 1
        
        # Run environment agents
        try:
            env_evidence = self.run_environment_agents()
            if self.post_evidence(env_evidence):
                results["environment"] = len(env_evidence)
        except Exception as e:
            logger.error(f"Environment agents error: {e}")
            results["errors"] += 1
        
        # Run emergency agents
        try:
            emergency_evidence = self.run_emergency_agents()
            if self.post_evidence(emergency_evidence):
                results["emergency"] = len(emergency_evidence)
        except Exception as e:
            logger.error(f"Emergency agents error: {e}")
            results["errors"] += 1
        
        return results
    
    def run_continuous(self):
        """Run agents continuously."""
        logger.info(f"🚀 Starting Enhanced GridWatch Agent Runner...")
        logger.info(f"  Backend URL: {self.backend_url}")
        logger.info(f"  Poll interval: {self.poll_interval} seconds")
        logger.info(f"  Bounding box: {self.bbox}")
        logger.info(f"  City: {self.city}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                start_time = time.time()
                
                # Run all agents
                results = self.run_all_agents()
                
                # Log results
                logger.info(f"📊 Agent run completed: {results}")
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"⏰ Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.info("⚠️ Agent run took longer than interval, continuing immediately")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Stopping agent runner...")
        except Exception as e:
            logger.error(f"💥 Fatal error in agent runner: {e}")
            raise

def main():
    """Main entry point."""
    # Check if backend is available
    backend_url = os.getenv('BACKEND_URL', 'https://gridwatch-backend-554454627121.us-east1.run.app')
    try:
        health_url = f"{backend_url}/health"
        response = requests.get(health_url, timeout=5)
        response.raise_for_status()
        logger.info(f"✅ Backend is healthy: {response.json()}")
    except Exception as e:
        logger.error(f"❌ Cannot connect to backend at {backend_url}: {e}")
        logger.error("Please start the backend first: uvicorn main:app --reload --port 8000")
        return
    
    # Check if API key is available (should be set in cloud environment)
    if not os.getenv('GOOGLE_API_KEY'):
        logger.warning("⚠️ GOOGLE_API_KEY not found in environment")
        logger.info("This is normal if running locally - the cloud backend has its own API key")
    
    # Run the agent runner
    runner = EnhancedAgentRunner()
    runner.run_continuous()

if __name__ == "__main__":
    main()
