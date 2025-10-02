# traffic_update_orchestrator/sub_agents/weather/agent.py

"""weather_agent – fetches Bengaluru weather via the ADK Google‐Search tool."""

from google.adk import Agent
from google.adk.tools import google_search

from . import weather_prompt   # imports WEATHER_PROMPT

MODEL = "gemini-2.5-pro"

weather_agent = Agent(
    model=MODEL,
    name="weather_agent",
    instruction=weather_prompt.WEATHER_PROMPT,
    output_key="weather_data",
    tools=[google_search],        # primary tool
)