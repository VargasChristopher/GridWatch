"""air_quality_agent – gathers air quality data and pollution alerts via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import air_quality_prompt

MODEL = "gemini-2.5-pro"

air_quality_agent = Agent(
    model=MODEL,
    name="air_quality_agent",
    instruction=air_quality_prompt.AIR_QUALITY_PROMPT,
    output_key="air_quality_alerts",
    tools=[google_search],
)
