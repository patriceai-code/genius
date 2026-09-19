"""
Tool: list_entities
Queries the Home Graph for registered devices, systems, and lifecycle status.
Powers the home overview and UI boards.
"""

from typing import Dict, Any, List, Optional


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
        Lists entities recorded in the Home Graph.
        """
        mock_entities: List[Dict[str, Any]] = [
            {
                "id": "ent_co_hallway",
                "type": "co_detector",
                "brand": "Kidde",
                "model": "KN-COPP-3",
                "location": "hallway",
                "lifecycle_state": "end_of_life",
                "manufacture_year": 2018,
                "confidence": 0.98,
                "provenance": "acoustic_diagnosis:incident_20261001",
                "updated_at": "2026-09-26T12:00:00Z"
            },
            {
                "id": "ent_smoke_kitchen",
                "type": "smoke_detector",
                "brand": "First Alert",
                "model": "BRK-9120B",
                "location": "kitchen",
                "lifecycle_state": "healthy",
                "manufacture_year": 2023,
                "confidence": 0.95,
                "provenance": "manual_registration:user_input",
                "updated_at": "2026-09-20T10:15:00Z"
            },
            {
                "id": "ent_furnace_basement",
                "type": "hvac_furnace",
                "brand": "Carrier",
                "model": "Infinity 98",
                "location": "basement",
                "lifecycle_state": "aging",
                "manufacture_year": 2015,
                "confidence": 0.90,
                "provenance": "inspection_tag:photo_20260901",
                "updated_at": "2026-09-01T08:00:00Z"
            }
        ]

        filtered = mock_entities
        if lifecycle_state:
            filtered = [e for e in filtered if e["lifecycle_state"] == lifecycle_state]
        if location:
            filtered = [e for e in filtered if e["location"].lower() == location.lower()]

        return {
            "total_entities": len(filtered),
            "entities": filtered
        }
