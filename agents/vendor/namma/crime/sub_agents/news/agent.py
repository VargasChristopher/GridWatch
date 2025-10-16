"""crime_news_agent – gathers crime reports from news sources via Google Search."""

from google.adk import Agent
from google.adk.tools import google_search

from . import news_prompt

MODEL = "gemini-2.5-pro"

crime_news_agent = Agent(
    model=MODEL,
    name="crime_news_agent",
    instruction=news_prompt.CRIME_NEWS_PROMPT,
    output_key="crime_news_reports",
    tools=[google_search],
)
