"""
Tool: diagnose
Matches extracted features or clip against beepdb signatures.
Identifies hardware device, failure state, severity, and generates an action proposal.
"""

from typing import Dict, Any, Optional
import os

from audio.matcher import match_acoustic_features


def register_diagnose(server):
    @server.tool(
        name="diagnose",
        description="Diagnoses an acoustic pattern against known device beep codes. Returns device identity, failure diagnosis, confidence score, and candidate action proposal."
    )
    def diagnose(
        interval_s: float = 30.0,
        peak_freq_hz: float = 3200.0,
        duration_ms: float = 80.0,
        location: str = "hallway",
        clip_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates acoustic signatures against device registry.
        """
        match = match_acoustic_features(interval_s, peak_freq_hz, duration_ms)

        if not match:
            return {
                "entity_id": "ent_unknown",
                "device_class": "unknown",
                "brand": "Unknown",
                "location": location,
                "meaning": "unrecognized_cadence",
                "severity": "info",
                "confidence": 0.0,
                "spoken_summary": "I heard a sound, but it does not match any known device error codes in the library.",
                "proposal": None
            }

        entity_id = f"ent_{match.device_class}_{location.lower()}"
        match_dict = match.to_dict(location=location)

        proposal_kind = "order_replacement" if match.meaning == "end_of_life" else "replace_battery"
        proposal_action = "Order Replacement Unit ($34.99)" if match.meaning == "end_of_life" else "Order 9V Batteries / Walkthrough"

        proposal = {
            "id": f"prop_{match.device_class}_{match.meaning[:8]}_01",
            "kind": proposal_kind,
            "status": "proposed",
            "title": proposal_action,
            "device": f"{match.brand} {match.device_class.replace('_', ' ').title()}",
            "requires_confirmation": True
        }

        return {
            "entity_id": entity_id,
            "device_class": match.device_class,
            "brand": match.brand,
            "location": location,
            "meaning": match.meaning,
            "severity": match.severity,
            "confidence": match.confidence,
            "recommended_action": match.action,
            "spoken_summary": match_dict["spoken_summary"],
            "proposal": proposal,
            "source_provenance": f"manufacturer_manual:{match.source_url}",
            "expected_specs": match_dict["expected_specs"]
        }
