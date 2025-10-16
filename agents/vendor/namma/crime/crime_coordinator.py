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

from sub_agents.police.agent import police_agent
from sub_agents.news.agent import crime_news_agent
from sub_agents.social_media.agent import crime_social_agent
import prompt

# Use environment variable or default to gemini-2.5-pro
MODEL = os.getenv("CRIME_AGENT_MODEL", "gemini-2.5-pro")

warnings.filterwarnings("ignore", message="there are non-text parts in the response:")

logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrimeIncident(BaseModel):
    timestamp: str
    location: str
    incident_type: str
    severity: str
    description: str
    source: str
    advice: str

class CrimeDigestOutput(BaseModel):
    crime_digest: Any = Field(
        description="Array of crime incidents with timestamp, location, type, severity, etc."
    )

    @field_validator("crime_digest", mode="after")
    @classmethod
    def validate_crime_digest(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)

# Coordinator agent definition
crime_coordinator = LlmAgent(
    name="crime_coordinator",
    model=MODEL,
    description="Aggregates police reports, news, and social feeds for a comprehensive crime and safety snapshot",
    instruction=prompt.CRIME_COORDINATOR_PROMPT,
    output_key="crime_digest",
    tools=[
        AgentTool(agent=police_agent),
        AgentTool(agent=crime_news_agent),
        AgentTool(agent=crime_social_agent),
    ],
)

# Default for `adk run`
root_agent = crime_coordinator

# — Runner setup —
session_service = InMemorySessionService()
runner = Runner(
    agent=crime_coordinator,
    app_name="crime_monitoring_orchestrator",
    session_service=session_service,
)

async def _run_and_clean(user_input: str) -> CrimeDigestOutput:
    # 1) Create & await a fresh session
    session_id = uuid.uuid4().hex
    await session_service.create_session(
        app_name="crime_monitoring_orchestrator",
        user_id="crime_user",
        session_id=session_id,
    )

    # 2) Build the user message
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    # 3) Stream events until final response
    raw_response = None
    async for event in runner.run_async(
        user_id="crime_user",
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
    logger.info(f"Crime coordinator response: {payload}")
    
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        return CrimeDigestOutput(crime_digest=[])

    return CrimeDigestOutput.model_validate(payload, strict=False)

def get_crime_digest(user_input: str) -> CrimeDigestOutput:
    """
    Synchronous wrapper for getting crime digest.
    Args:
        user_input: Natural language request for crime information
    Returns:
        CrimeDigestOutput containing crime incidents
    """
    return asyncio.run(_run_and_clean(user_input))
