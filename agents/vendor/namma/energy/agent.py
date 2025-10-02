"""
agent.py – BESCOMOutageAgent (prompt fixed in agent_config.json).
`location` is guaranteed to be List[str] with one element per locality.
"""

from __future__ import annotations

import asyncio, json, logging, re
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Iterable, List,Any

from pydantic import BaseModel, ValidationError, ConfigDict, Field,field_validator
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from tools import gt

# ── configuration -----------------------------------------------------------
_DEFAULT_PROMPT = json.loads(
    Path(__file__).with_name("agent_config.json").read_text()
)["default_prompt"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Location(BaseModel):
    location: List[str]
    start_time: datetime
    end_time: datetime | None
    reason: str

# ── pydantic model ----------------------------------------------------------
class OutageSummary(BaseModel):
    outage_summary: Any = Field(geoFenceData=Location)

    @field_validator("outage_summary", mode="after")
    @classmethod
    def validate_location_weather(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)

# ── agent -------------------------------------------------------------------
class BESCOMOutageAgent(BaseAgent):
    model_config = ConfigDict(extra="allow")

    def __init__(self) -> None:
        super().__init__(name="BESCOMOutageAgent")
        self.prompt = _DEFAULT_PROMPT

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        raw = await asyncio.to_thread(gt.ask_json, self.prompt)
        records = OutageSummary(**raw)
        payload = json.dumps(
            [r.model_dump() for r in records], indent=2, default=str
        )
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=payload)]),
            partial=False,
        )


# ── factory -----------------------------------------------------------------
def make_bescom_agent() -> BESCOMOutageAgent:
    return BESCOMOutageAgent()
