"""police_agent – gathers real-time crime reports from official police sources via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import police_prompt

MODEL = "gemini-2.5-pro"

police_agent = Agent(
    model=MODEL,
    name="police_agent",
    instruction=police_prompt.POLICE_PROMPT,
    output_key="police_reports",
    tools=[google_search],
)
