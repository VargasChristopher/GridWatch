import re
import json
import uuid
import asyncio
import logging
import warnings
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field, field_validator
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types , errors # for Content / Part

from sub_agents.bbmp.agent import bbmp_agent
from sub_agents.btp.agent import btp_agent
from sub_agents.social_media.agent import social_media_agent
from sub_agents.weather.agent import weather_agent
import prompt

MODEL = "gemini-2.5-pro"

warnings.filterwarnings("ignore", message="there are non-text parts in the response:")

logging.getLogger("google.genai").setLevel(logging.ERROR)

class WeatherEntry(BaseModel):
    location: Any
    temperature: Any
    conditions: Any
    precipitation: Any
    wind: Any

class TrafficDigestOutput(BaseModel):
    bengaluru_traffic_digest: Any = Field(
        timestamp=str,
        location=str,
        summary=str,
        severity_reason=str,
        delay=str,
        advice=str,
    )
    location_weather: Any = Field(
        weather_summary=WeatherEntry
    )  # <— just raw strings

    @field_validator("location_weather", mode="after")
    @classmethod
    def validate_location_weather(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)
# Coordinator agent definition
traffic_coordinator = LlmAgent(
    name="traffic_coordinator",
    model=MODEL,
    description="Aggregates BBMP, BTP, social feeds, and weather for a Bengaluru traffic snapshot",
    instruction=prompt.TRAFFIC_COORDINATOR_PROMPT,
    output_key="bengaluru_traffic_digest",
    tools=[
        AgentTool(agent=bbmp_agent),
        AgentTool(agent=btp_agent),
        AgentTool(agent=social_media_agent),
        AgentTool(agent=weather_agent),
    ],
)

# Default for `adk run`
root_agent = traffic_coordinator


# — Runner setup —
session_service = InMemorySessionService()
runner = Runner(
    agent=traffic_coordinator,
    app_name="traffic_update_orchestrator",
    session_service=session_service,
)

async def _run_and_clean(user_input: str) -> TrafficDigestOutput:
    # 1) Create & await a fresh session
    session_id = uuid.uuid4().hex
    await session_service.create_session(
        app_name="traffic_update_orchestrator",
        user_id="traffic_user",
        session_id=session_id,
    )

    # 2) Build the user message
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    # 3) Stream events until final response
    raw_response = None
    async for event in runner.run_async(
        user_id="traffic_user",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            raw_response = event.content.parts[0].text
            break

    if raw_response is None:
        raise RuntimeError("Agent did not emit a final response")
    # 4) Extract JSON payload

    payload = re.sub(r"^```json\n|```", "", raw_response, flags=re.DOTALL)
    print(f" response: {payload}")
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        return TrafficDigestOutput(bengaluru_traffic_digest=[],location_weather=[])
    
    return TrafficDigestOutput.model_validate(payload,strict=False)

    # — Coerce any dict entries in location_weather into JSON strings —
    # if "location_weather" in payload:
    #     coerced = []
    #     for entry in payload["location_weather"]:
    #         if isinstance(entry, dict):
    #             # turn dict into a compact JSON string
    #             coerced.append(json.dumps(entry, separators=(",", ":")))
    #         else:
    #             coerced.append(str(entry))
    #     payload["location_weather"] = coerced

    # # 5) Validate and return the structured output
    # return TrafficDigestOutput.parse_obj(payload)



def get_traffic_digest(user_input: str) -> TrafficDigestOutput:
    return asyncio.run(_run_and_clean(user_input))