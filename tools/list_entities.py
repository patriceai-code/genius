"""
Tool: list_entities
Queries the Home Graph for registered devices, systems, and lifecycle status.
Powers the home overview and UI boards.
"""

from typing import Dict, Any, List, Optional
from graph.store import GRAPH_STORE


def register_list_entities(server):
    @server.tool(
        name="list_entities",
        description="Retrieves registered home devices, detectors, and infrastructure components with their current lifecycle state and data provenance."
    )
    def list_entities(
        lifecycle_state: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lists entities recorded in the persistent Home Graph.
        """
        entities = GRAPH_STORE.list_entities(lifecycle_state=lifecycle_state)
        if location:
            entities = [e for e in entities if e["location"].lower() == location.lower()]

        return {
            "total_entities": len(entities),
            "entities": entities
        }
