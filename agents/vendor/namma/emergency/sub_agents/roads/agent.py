# ---------- sub_agents/roads/agent.py ----------
"""Roads Emergency Agent - Detects and reports road closures and traffic emergencies."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool

from . import roads_prompt

# Roads emergency agent definition
roads_agent = LlmAgent(
    name="roads_emergency_agent",
    model=os.getenv("ROADS_AGENT_MODEL", "gemini-2.5-flash"),
    description="Monitors road closures, accidents, and traffic emergencies",
    instruction=roads_prompt.ROADS_AGENT_PROMPT,
    tools=[google_search_tool.GoogleSearchTool()],
)
