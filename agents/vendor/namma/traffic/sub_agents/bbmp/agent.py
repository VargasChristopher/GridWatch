"""bbmp_agent – gathers real-time Bengaluru traffic / civic-works updates via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import bbmp_prompt  # ⇨ imports BBMP_PROMPT

MODEL = "gemini-2.5-pro"

bbmp_agent = Agent(
    model=MODEL,
    name="bbmp_agent",
    instruction=bbmp_prompt.BBMP_PROMPT,
    output_key="bbmp_updates",
    tools=[google_search],          # ← switched to Google Search
)