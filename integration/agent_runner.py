#!/usr/bin/env python3
"""
Unified Agent Runner for GridWatch
Continuously runs all agents and posts evidence to the backend.
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

class AgentRunner:
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.poll_interval = int(os.getenv('AGENT_POLL_INTERVAL', '60'))  # seconds
        self.bbox = os.getenv('GRIDWATCH_BBOX', '-77.044,38.895,-77.028,38.905')
        self.city = os.getenv('GRIDWATCH_CITY', 'Washington, DC')
        
    def run_traffic_agents(self) -> List[Dict[str, Any]]:
        """Run traffic orchestrator and return evidence."""
        try:
            logger.info("Running traffic agents...")
            
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
            logger.info("Running energy agents...")
            
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
    
    def run_gridwatch_agents(self) -> List[Dict[str, Any]]:
        """Run GridWatch core orchestrator and return evidence."""
        try:
            logger.info("Running GridWatch core orchestrator...")
            
            # Skip GridWatch agents if no Google Cloud credentials
            if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.info("Skipping GridWatch agents - no Google Cloud credentials found")
                return []
            
            # Change to GridWatch agents directory
            gridwatch_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'gridwatch_agents', 'src')
            original_cwd = os.getcwd()
            os.chdir(gridwatch_dir)
            
            try:
                # Add GridWatch directory to Python path
                sys.path.insert(0, gridwatch_dir)
                # Dynamic import to avoid path issues
                from run_orchestrator import main as run_gridwatch_orchestrator
                
                # The GridWatch orchestrator posts directly to Firestore
                # We just need to run it - it doesn't return evidence for our backend
                run_gridwatch_orchestrator()
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
            # Return empty since GridWatch posts to its own Firestore collection
            return []
            
        except Exception as e:
            logger.error(f"Error running GridWatch agents: {e}")
            return []
    
    def post_evidence(self, evidence_items: List[Dict[str, Any]]) -> bool:
        """Post evidence to backend."""
        if not evidence_items:
            return True
            
        try:
            response = requests.post(f"{self.backend_url}/evidence", json=evidence_items, timeout=10)
            response.raise_for_status()
            logger.info(f"Posted {len(evidence_items)} evidence items to backend: {response.json()}")
            return True
        except Exception as e:
            logger.error(f"Error posting evidence to backend: {e}")
            return False
    
    def run_all_agents(self) -> Dict[str, int]:
        """Run all agents and return counts."""
        results = {"traffic": 0, "energy": 0, "gridwatch": 0, "errors": 0}
        
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
        
        # Run GridWatch core orchestrator
        try:
            self.run_gridwatch_agents()
            results["gridwatch"] = 1  # GridWatch posts to its own Firestore collection
        except Exception as e:
            logger.error(f"GridWatch agents error: {e}")
            results["errors"] += 1
        
        return results
    
    def run_continuous(self):
        """Run agents continuously."""
        logger.info(f"Starting GridWatch Agent Runner...")
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
                logger.info(f"Agent run completed: {results}")
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.info("Agent run took longer than interval, continuing immediately")
                    
        except KeyboardInterrupt:
            logger.info("Stopping agent runner...")
        except Exception as e:
            logger.error(f"Fatal error in agent runner: {e}")
            raise

def main():
    """Main entry point."""
    # Check if backend is available
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    try:
        health_url = f"{backend_url}/health"
        response = requests.get(health_url, timeout=5)
        response.raise_for_status()
        logger.info(f"Backend is healthy: {response.json()}")
    except Exception as e:
        logger.error(f"Cannot connect to backend at {backend_url}: {e}")
        logger.error("Please start the backend first: uvicorn main:app --reload --port 8000")
        return
    
    # Run the agent runner
    runner = AgentRunner()
    runner.run_continuous()

if __name__ == "__main__":
    main()
