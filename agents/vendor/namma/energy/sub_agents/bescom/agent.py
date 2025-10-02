from google.adk import Agent
from google.adk.tools import google_search

from . import bescom_prompt  # BESCOM_PROMPT string

MODEL = "gemini-2.5-pro"

bescom_agent = Agent(
    model=MODEL,
    name="bescom_agent",
    instruction=bescom_prompt.BESCOM_PROMPT,
    output_key="bescom_outages",
    tools=[google_search],
) 