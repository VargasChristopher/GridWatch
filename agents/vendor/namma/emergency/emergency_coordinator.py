# ---------- emergency_coordinator.py ----------
"""
Emergency Coordinator Agent for GridWatch.

Orchestrates three specialized emergency sub-agents:
1. Roads Emergency Agent - Road closures and traffic emergencies
2. Escorts Emergency Agent - Emergency services operations
3. Public Alerts Agent - Official emergency alerts

All agents run in parallel and results are aggregated into a unified emergency digest.
"""

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

from sub_agents.roads.agent import roads_agent
from sub_agents.escorts.agent import escorts_agent
from sub_agents.public_alerts.agent import public_alerts_agent
import prompt

# Use environment variable or default to gemini-2.5-flash (cheaper, faster)
MODEL = os.getenv("EMERGENCY_AGENT_MODEL", "gemini-2.5-flash")

warnings.filterwarnings("ignore", message="there are non-text parts in the response:")

logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyIncident(BaseModel):
    type: str
    severity: float
    confidence: float
    location: str
    description: str
    source: str
    updated_at: str

class EmergencyDigestOutput(BaseModel):
    emergency_digest: Any = Field(
        description="Array of emergency incidents and alerts"
    )

    @field_validator("emergency_digest", mode="after")
    @classmethod
    def validate_emergency_digest(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)

# Coordinator agent definition
emergency_coordinator = LlmAgent(
    name="emergency_coordinator",
    model=MODEL,
    description="Aggregates road closures, emergency services operations, and public alerts for comprehensive emergency monitoring",
    instruction=prompt.EMERGENCY_COORDINATOR_PROMPT,
    output_key="emergency_digest",
    tools=[
        AgentTool(agent=roads_agent),
        AgentTool(agent=escorts_agent),
        AgentTool(agent=public_alerts_agent),
    ],
)

# Default for `adk run`
root_agent = emergency_coordinator

# — Runner setup —
session_service = InMemorySessionService()
runner = Runner(
    agent=emergency_coordinator,
    app_name="emergency_monitoring_orchestrator",
    session_service=session_service,
)

async def _run_and_clean(user_input: str) -> EmergencyDigestOutput:
    # 1) Create & await a fresh session
    session_id = uuid.uuid4().hex
    await session_service.create_session(
        app_name="emergency_monitoring_orchestrator",
        user_id="emergency_user",
        session_id=session_id,
    )

    # 2) Build the user message
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    # 3) Stream events until final response
    raw_response = None
    async for event in runner.run_async(
        user_id="emergency_user",
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
    logger.info(f"Emergency coordinator response: {payload}")
    
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        return EmergencyDigestOutput(emergency_digest=[])

    return EmergencyDigestOutput.model_validate(payload, strict=False)

def get_emergency_digest(user_input: str) -> EmergencyDigestOutput:
    """
    Synchronous wrapper for getting emergency digest.
    Args:
        user_input: Natural language request for emergency information
    Returns:
        EmergencyDigestOutput containing aggregated emergency incidents
    """
    return asyncio.run(_run_and_clean(user_input))
