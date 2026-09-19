"""
Tool: get_home_health
Returns high-level graph summary: healthy/aging/eol counts and open incidents.
Generates the MCP Apps card payload for visual display on Echo Show / Tablet.
"""

from typing import Dict, Any


def register_get_home_health(server):
    @server.tool(
        name="get_home_health",
        description="Generates an aggregate Home Health scorecard and visual MCP Apps card payload summarizing device lifecycles, urgent incidents, and warranty status."
    )
    def get_home_health() -> Dict[str, Any]:
        """
        Calculates and formats home health metrics.
        """
        return {
            "health_score": 82,  # 0 to 100
            "status": "attention_required",
            "summary": "1 critical device reached end-of-life (hallway CO detector); 1 aging HVAC system.",
            "metrics": {
                "total_monitored_devices": 14,
                "healthy_count": 12,
                "aging_count": 1,
                "end_of_life_count": 1,
                "open_incidents": 1
            },
            "urgent_incidents": [
                {
                    "incident_id": "inc_20261001_01",
                    "device": "Kidde CO Detector",
                    "location": "hallway",
                    "issue": "End-of-life sensor expiration (chirping every 30s)",
                    "severity": "critical",
                    "action_status": "replacement_proposed"
                }
            ],
            "card_payload": {
                "template": "mcp.apps.card.home_health",
                "title": "Home Health Overview",
                "accent_color": "#FF9900",  # Amazon Amber
                "gauges": [
                    {"label": "Healthy", "value": 12, "color": "#00A86B"},
                    {"label": "Aging", "value": 1, "color": "#F4B400"},
                    {"label": "End of Life", "value": 1, "color": "#DB4437"}
                ]
            }
        }
