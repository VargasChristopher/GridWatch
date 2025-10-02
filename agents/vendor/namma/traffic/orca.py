import json
import asyncio
import logging
from typing import AsyncGenerator, List
from agents import road_block_agent, accident_agent, environment_agent

from google.adk.agents import LlmAgent, BaseAgent, Runner
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
        super().__init__(name=name, sub_agents=sub_agents)
        self.road_block_agent = road_block_agent
        self.accident_agent = accident_agent
        self.environment_agent = environment_agent

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Starting traffic update workflow.")
        results = await asyncio.gather(
            self._run_agent(self.road_block_agent, ctx, details="Road block details"),
            self._run_agent(self.accident_agent, ctx, details="Accident details"),
            self._run_agent(self.environment_agent, ctx, metrics="Weather, Visibility"),
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
        async for event in agent.run_async(ctx, **kwargs):
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
    
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Final response: {event.content.parts[0].text}")
        print(event)

if __name__ == "__main__":
    asyncio.run(call_traffic_update_agent_async("Traffic update alert: road block detected."))