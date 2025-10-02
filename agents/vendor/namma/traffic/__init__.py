"""
Package init – exposes the coordinator as `root_agent` for ADK.
"""

from .traffic_coordinator import traffic_coordinator  # relative import ✔️

root_agent = traffic_coordinator

