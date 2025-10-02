import re
import json
import uuid
import asyncio
import logging
import warnings

from pydantic import BaseModel, Field
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from sub_agents.bescom.agent import bescom_agent
import prompt
from pubsub import publish_messages

MODEL = "gemini-2.5-pro"

warnings.filterwarnings("ignore", message="there are non-text parts in the response:")

logging.getLogger("google.genai").setLevel(logging.ERROR)

class OutageEntry(BaseModel):
    locations: list[str]
    start_time: str
    end_time: str | None
    reason: str

class EnergyDigestOutput(BaseModel):
    outage_summary: Any = Field(
        description="Array of outage entries with timestamp, summary, etc."
    )

# Coordinator agent definition
energy_coordinator = LlmAgent(
    name="energy_coordinator",
    model=MODEL,
    description="Aggregates BESCOM, news, and social feeds for a Bengaluru power-outage snapshot",
    instruction=prompt.ENERGY_COORDINATOR_PROMPT,
    output_key="outage_summary",
    tools=[
        AgentTool(agent=bescom_agent),
        # Additional tools can be added later (e.g. social media)
    ],
)

# Default for `adk run`
root_agent = energy_coordinator

# — Runner setup —
session_service = InMemorySessionService()
runner = Runner(
    agent=energy_coordinator,
    app_name="energy_management_orchestrator",
    session_service=session_service,
)

async def _run_and_clean(user_input: str) -> EnergyDigestOutput:
    session_id = uuid.uuid4().hex
    await session_service.create_session(
        app_name="energy_management_orchestrator",
        user_id="energy_user",
        session_id=session_id,
    )

    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    raw_response = None
    async for event in runner.run_async(
        user_id="energy_user",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            raw_response = event.content.parts[0].text
            break

    if raw_response is None:
        raise RuntimeError("Agent did not emit a final response")

    payload = re.sub(r"^```json\n|```", "", raw_response, flags=re.DOTALL)
    print(f" response: {payload}")
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        return EnergyDigestOutput(outage_summary=[])

    return EnergyDigestOutput.model_validate(payload, strict=False)


def get_energy_digest(user_input: str) -> EnergyDigestOutput:
    return asyncio.run(_run_and_clean(user_input)) 