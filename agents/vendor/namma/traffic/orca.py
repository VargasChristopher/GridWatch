import json
import os
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Any
import time
import requests
from agents import road_block_agent, accident_agent, environment_agent

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.runners import Runner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_agent_config(config_file: str = 'agent_config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    config_map = {}
    for agent in config.get("agents", []):
        if "RoadBlock" in agent["name"]:
            config_map["road_block"] = agent
        elif "Accident" in agent["name"]:
            config_map["accident"] = agent
        elif "Environment" in agent["name"]:
            config_map["environment"] = agent
    return config_map

class TrafficUpdateOrchestratorAgent(BaseAgent):
    """
    This orchestrator concurrently invokes RoadBlockAgent, AccidentAgent, and EnvironmentAgent.
    """
    road_block_agent: LlmAgent
    accident_agent: LlmAgent
    environment_agent: LlmAgent

    def __init__(self,
                 name: str,
                 road_block_agent: LlmAgent,
                 accident_agent: LlmAgent,
                 environment_agent: LlmAgent):
        sub_agents = [road_block_agent, accident_agent, environment_agent]
        super().__init__(
            name=name,
            sub_agents=sub_agents,
            road_block_agent=road_block_agent,
            accident_agent=accident_agent,
            environment_agent=environment_agent,
        )
        self.road_block_agent = road_block_agent
        self.accident_agent = accident_agent
        self.environment_agent = environment_agent

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Starting traffic update workflow.")
        results = await asyncio.gather(
            self._run_agent(self.road_block_agent, ctx),
            self._run_agent(self.accident_agent, ctx),
            self._run_agent(self.environment_agent, ctx),
            return_exceptions=True
        )
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Agent execution error: {res}")
            else:
                for event in res:
                    yield event
        logger.info(f"[{self.name}] Completed traffic update workflow.")

    async def _run_agent(self, agent: LlmAgent, ctx: InvocationContext, **kwargs) -> List[Event]:
        events = []
        async for event in agent.run_async(ctx):
            events.append(event)
        return events

config_map = load_agent_config('agent_config.json')
logger.info(f"Loaded agent configuration: {config_map}")

traffic_update_agent = TrafficUpdateOrchestratorAgent(
    name="TrafficUpdateOrchestratorAgent",
    road_block_agent=road_block_agent,
    accident_agent=accident_agent,
    environment_agent=environment_agent,
)

INITIAL_STATE = {
    "details": "Initial traffic update input",
    "metrics": "Initial environmental metrics",
}

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="traffic_app",
        user_id="user_001",
        session_id="session_001",
        state=INITIAL_STATE
    )
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=traffic_update_agent,
        app_name="traffic_app",
        session_service=session_service
    )
    return session_service, runner

# --------------- Bridge Helpers ---------------
def _bbox_center() -> tuple[float, float]:
    raw = os.getenv("GRIDWATCH_BBOX", "-77.044,38.895,-77.028,38.905")
    try:
        if raw.strip().startswith("["):
            v = json.loads(raw)
        else:
            v = [float(x) for x in raw.split(",")]
        min_lng, min_lat, max_lng, max_lat = v
        return ((min_lat + max_lat) / 2.0, (min_lng + max_lng) / 2.0)
    except Exception:
        return (38.9000, -77.0365)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _post_to_backend_as_evidence(state: dict[str, Any]) -> None:
    backend_url = os.getenv("BACKEND_URL", os.getenv("VITE_API_URL", "http://localhost:8000"))
    lat, lng = _bbox_center()

    evidence_items: List[Dict[str, Any]] = []

    if state.get("road_block_result"):
        evidence_items.append({
            "evidence_id": f"roadblock-{int(time.time())}",
            "source_type": "news",
            "type": "road_closure",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 100,
            "confidence": 0.7,
            "url": None,
            "raw": {"agent": "RoadBlockAgent", "text": state.get("road_block_result")},
            "detected_at": _now_iso(),
        })

    if state.get("accident_result"):
        evidence_items.append({
            "evidence_id": f"accident-{int(time.time())}",
            "source_type": "news",
            "type": "accident",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 80,
            "confidence": 0.75,
            "url": None,
            "raw": {"agent": "AccidentAgent", "text": state.get("accident_result")},
            "detected_at": _now_iso(),
        })

    if state.get("environment_result"):
        evidence_items.append({
            "evidence_id": f"env-{int(time.time())}",
            "source_type": "news",
            "type": "congestion",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 120,
            "confidence": 0.6,
            "url": None,
            "raw": {"agent": "EnvironmentAgent", "text": state.get("environment_result")},
            "detected_at": _now_iso(),
        })

    if not evidence_items:
        logging.info("No agent outputs mapped to Evidence; skipping POST.")
        return

    resp = requests.post(f"{backend_url}/evidence", json=evidence_items, timeout=10)
    resp.raise_for_status()
    logging.info(f"Posted {len(evidence_items)} evidence items to backend: {resp.json()}")


async def call_traffic_update_agent_async(user_input: str):
    session_service, runner = await setup_session_and_runner()
    current_session = await session_service.get_session(
        app_name="traffic_app",
        user_id="user_001",
        session_id="session_001"
    )
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["user_input"] = user_input
    logger.info(f"User input: {user_input}")

    content = types.Content(role='user', parts=[types.Part(text=f"Process input: {user_input}")])
    events = runner.run_async(user_id="user_001", session_id="session_001", new_message=content)

    # Collect simple state from agent responses
    final_state: Dict[str, Any] = {}
    async for event in events:
        # Log final text for visibility
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Final response: {event.content.parts[0].text}")
        # Merge any state deltas the agents emit
        try:
            delta = getattr(event, "actions", None)
            if delta and getattr(delta, "state_delta", None):
                for k, v in delta.state_delta.items():
                    final_state[k] = v
        except Exception:
            pass
        print(event)

    # Bridge: convert agent outputs -> Evidence[] and POST to backend
    try:
        _post_to_backend_as_evidence(final_state)
    except Exception as e:
        logger.error(f"Failed to bridge agent outputs to backend: {e}")

if __name__ == "__main__":
    asyncio.run(call_traffic_update_agent_async("Traffic update alert: road block detected."))


# --------------- Bridge Helpers ---------------
def _bbox_center() -> tuple[float, float]:
    raw = os.getenv("GRIDWATCH_BBOX", "-77.044,38.895,-77.028,38.905")
    try:
        # Support both JSON and CSV formats
        if raw.strip().startswith("["):
            v = json.loads(raw)
        else:
            v = [float(x) for x in raw.split(",")]
        min_lng, min_lat, max_lng, max_lat = v
        return ( (min_lat + max_lat) / 2.0, (min_lng + max_lng) / 2.0 )
    except Exception:
        return (38.9000, -77.0365)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _post_to_backend_as_evidence(state: Dict[str, Any]) -> None:
    """Create minimal Evidence[] from agent final state and POST to backend."""
    backend_url = os.getenv("BACKEND_URL", os.getenv("VITE_API_URL", "http://localhost:8000"))
    lat, lng = _bbox_center()

    evidence_items: List[Dict[str, Any]] = []

    # Map agent result texts into coarse incident types
    if state.get("road_block_result"):
        evidence_items.append({
            "evidence_id": f"roadblock-{int(time.time())}",
            "source_type": "news",
            "type": "road_closure",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 100,
            "confidence": 0.7,
            "url": None,
            "raw": {"agent": "RoadBlockAgent", "text": state.get("road_block_result")},
            "detected_at": _now_iso(),
        })

    if state.get("accident_result"):
        evidence_items.append({
            "evidence_id": f"accident-{int(time.time())}",
            "source_type": "news",
            "type": "accident",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 80,
            "confidence": 0.75,
            "url": None,
            "raw": {"agent": "AccidentAgent", "text": state.get("accident_result")},
            "detected_at": _now_iso(),
        })

    if state.get("environment_result"):
        # Treat environment signals as congestion hints
        evidence_items.append({
            "evidence_id": f"env-{int(time.time())}",
            "source_type": "news",
            "type": "congestion",
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": 120,
            "confidence": 0.6,
            "url": None,
            "raw": {"agent": "EnvironmentAgent", "text": state.get("environment_result")},
            "detected_at": _now_iso(),
        })

    if not evidence_items:
        logging.info("No agent outputs mapped to Evidence; skipping POST.")
        return

    resp = requests.post(f"{backend_url}/evidence", json=evidence_items, timeout=10)
    resp.raise_for_status()
    logging.info(f"Posted {len(evidence_items)} evidence items to backend: {resp.json()}")