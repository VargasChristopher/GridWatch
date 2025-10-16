"""weather_agent – gathers severe weather alerts and storm information via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import weather_prompt

MODEL = "gemini-2.5-pro"

weather_agent = Agent(
    model=MODEL,
    name="weather_agent",
    instruction=weather_prompt.WEATHER_PROMPT,
    output_key="weather_alerts",
    tools=[google_search],
)
