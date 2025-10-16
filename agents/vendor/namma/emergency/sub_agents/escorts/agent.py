# ---------- sub_agents/escorts/agent.py ----------
"""Escorts Emergency Agent - Detects and reports emergency services operations."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool

from . import escorts_prompt

# Escorts emergency agent definition
escorts_agent = LlmAgent(
    name="escorts_emergency_agent",
    model=os.getenv("ESCORTS_AGENT_MODEL", "gemini-2.5-flash"),
    description="Monitors emergency services operations and escorts",
    instruction=escorts_prompt.ESCORTS_AGENT_PROMPT,
    tools=[google_search_tool.GoogleSearchTool()],
)
