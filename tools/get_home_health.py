"""
Tool: get_home_health
Returns live Home Graph summary: healthy/aging/eol counts and open incidents.
Generates the MCP Apps card payload for visual display on Echo Show / Tablet.
"""

from typing import Dict, Any
from graph.store import GRAPH_STORE


def register_get_home_health(server):
    @server.tool(
        name="get_home_health",
        description="Generates an aggregate Home Health scorecard and visual MCP Apps card payload summarizing device lifecycles, urgent incidents, and warranty status."
    )
    def get_home_health() -> Dict[str, Any]:
        """
        Calculates live metrics from the persistent Home Graph.
        """
        return GRAPH_STORE.get_home_health()
