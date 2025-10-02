"""btp_agent – gathers real-time Bengaluru Traffic Police (BTP) alerts via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search 

from . import btp_prompt   # ⇨ imports BTP_PROMPT

MODEL = "gemini-2.5-pro"

btp_agent = Agent(
    model=MODEL,
    name="btp_agent",
    instruction=btp_prompt.BTP_PROMPT,
    output_key="btp_updates",
    tools=[google_search],        # ← primary tool
)
