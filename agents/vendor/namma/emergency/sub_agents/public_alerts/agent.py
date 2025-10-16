# ---------- sub_agents/public_alerts/agent.py ----------
"""Public Alerts Emergency Agent - Detects and reports public emergency alerts."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool

from . import public_alerts_prompt

# Public alerts emergency agent definition
public_alerts_agent = LlmAgent(
    name="public_alerts_emergency_agent",
    model=os.getenv("PUBLIC_ALERTS_AGENT_MODEL", "gemini-2.5-flash"),
    description="Monitors official emergency alerts and public notices",
    instruction=public_alerts_prompt.PUBLIC_ALERTS_AGENT_PROMPT,
    tools=[google_search_tool.GoogleSearchTool()],
)
