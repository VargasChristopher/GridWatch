"""environmental_alerts_agent – gathers flood, water, geological, and other environmental hazard alerts via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import environmental_alerts_prompt

MODEL = "gemini-2.5-pro"

environmental_alerts_agent = Agent(
    model=MODEL,
    name="environmental_alerts_agent",
    instruction=environmental_alerts_prompt.ENVIRONMENTAL_ALERTS_PROMPT,
    output_key="environmental_alerts",
    tools=[google_search],
)
