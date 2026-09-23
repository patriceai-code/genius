"""
MCP Apps Card Payloads
Generates structured visual cards rendered both in the Device Simulator client
and on real Alexa+ visual surfaces (Echo Show 8/10/15).
"""

from typing import Dict, Any, List


def render_home_health_card(
    score: int,
    healthy_count: int,
    aging_count: int,
    eol_count: int,
    urgent_incidents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Formats visual Home Health Scorecard."""
    accent = "#00C853" if score >= 90 else ("#FF9900" if score >= 70 else "#FF5252")

    return {
        "$schema": "https://mcp.spec/ui/card/v1.json",
        "card_type": "home_health_board",
        "title": "Home Infrastructure Health",
        "score": score,
        "accent_color": accent,
        "gauges": [
            {"label": "Healthy", "value": healthy_count, "color": "#00C853"},
            {"label": "Aging", "value": aging_count, "color": "#FF9900"},
            {"label": "End of Life", "value": eol_count, "color": "#FF5252"}
        ],
        "urgent_incidents": urgent_incidents,
        "last_updated": "live"
    }


def render_evidence_card(
    device_name: str,
    location: str,
    confidence: float,
    interval_s: float,
    peak_freq_hz: float,
    duration_ms: float,
    source_documentation: str,
    proposal_id: str
) -> Dict[str, Any]:
    """Formats Acoustic Evidence Card with physical signal markers."""
    return {
        "$schema": "https://mcp.spec/ui/card/v1.json",
        "card_type": "acoustic_evidence",
        "title": f"Acoustic Evidence: {device_name}",
        "location": location,
        "confidence_percentage": int(confidence * 100),
        "metrics": {
            "interval_cadence": f"{interval_s:.1f}s",
            "peak_frequency": f"{peak_freq_hz / 1000.0:.2f} kHz",
            "pulse_duration": f"{duration_ms:.0f} ms"
        },
        "retention_status": "Discarded In-Flight (Zero Raw Persistence)",
        "source_documentation": source_documentation,
        "action_proposal": {
            "proposal_id": proposal_id,
            "status": "awaiting_user_confirmation"
        }
    }
