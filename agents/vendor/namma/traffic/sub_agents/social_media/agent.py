"""social_media_agent – crowdsources real-time Bengaluru traffic posts via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import social_media_prompt   # ⇨ imports SOCIAL_MEDIA_PROMPT

MODEL = "gemini-2.5-pro"

social_media_agent = Agent(
    model=MODEL,
    name="social_media_agent",
    instruction=social_media_prompt.SOCIAL_MEDIA_PROMPT,
    output_key="social_media_updates",
    tools=[google_search],          # ← primary discovery tool
)
