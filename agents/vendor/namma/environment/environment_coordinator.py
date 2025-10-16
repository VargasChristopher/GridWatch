import re
import json
import uuid
import asyncio
import logging
import warnings
import os

from pydantic import BaseModel, Field, field_validator
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types, errors

from sub_agents.weather.agent import weather_agent
from sub_agents.air_quality.agent import air_quality_agent
from sub_agents.environmental_alerts.agent import environmental_alerts_agent
import prompt

# Use environment variable or default to gemini-2.5-flash (cheaper, faster)
MODEL = os.getenv("ENVIRONMENT_AGENT_MODEL", "gemini-2.5-flash")

warnings.filterwarnings("ignore", message="there are non-text parts in the response:")

logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentalHazard(BaseModel):
    timestamp: str
    location: str
    hazard_type: str
    severity: str
    description: str
    source: str
    advice: str

class EnvironmentDigestOutput(BaseModel):
    environment_digest: Any = Field(
        description="Array of environmental hazards and alerts"
    )

    @field_validator("environment_digest", mode="after")
    @classmethod
    def validate_environment_digest(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)

# Coordinator agent definition
environment_coordinator = LlmAgent(
    name="environment_coordinator",
    model=MODEL,
    description="Aggregates weather alerts, air quality, and environmental hazards for comprehensive environmental monitoring",
    instruction=prompt.ENVIRONMENT_COORDINATOR_PROMPT,
    output_key="environment_digest",
    tools=[
        AgentTool(agent=weather_agent),
        AgentTool(agent=air_quality_agent),
        AgentTool(agent=environmental_alerts_agent),
    ],
)

# Default for `adk run`
root_agent = environment_coordinator

# — Runner setup —
session_service = InMemorySessionService()
runner = Runner(
    agent=environment_coordinator,
    app_name="environment_monitoring_orchestrator",
    session_service=session_service,
)

async def _run_and_clean(user_input: str) -> EnvironmentDigestOutput:
    # 1) Create & await a fresh session
    session_id = uuid.uuid4().hex
    await session_service.create_session(
        app_name="environment_monitoring_orchestrator",
        user_id="environment_user",
        session_id=session_id,
    )

    # 2) Build the user message
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    # 3) Stream events until final response
    raw_response = None
    async for event in runner.run_async(
        user_id="environment_user",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            raw_response = event.content.parts[0].text
            break

    if raw_response is None:
        raise RuntimeError("Agent did not emit a final response")

    # 4) Strip markdown fences and parse JSON
    payload = re.sub(r"^```json\n|```", "", raw_response, flags=re.DOTALL)
    logger.info(f"Environment coordinator response: {payload}")
    
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        return EnvironmentDigestOutput(environment_digest=[])

    return EnvironmentDigestOutput.model_validate(payload, strict=False)

def get_environment_digest(user_input: str) -> EnvironmentDigestOutput:
    """
    Synchronous wrapper for getting environment digest.
    Args:
        user_input: Natural language request for environmental information
    Returns:
        EnvironmentDigestOutput containing environmental hazards and alerts
    """
    return asyncio.run(_run_and_clean(user_input))
