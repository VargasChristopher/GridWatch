"""crime_social_agent – gathers crime reports from social media via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import social_media_prompt

MODEL = "gemini-2.5-pro"

crime_social_agent = Agent(
    model=MODEL,
    name="crime_social_agent",
    instruction=social_media_prompt.CRIME_SOCIAL_PROMPT,
    output_key="crime_social_reports",
    tools=[google_search],
)
