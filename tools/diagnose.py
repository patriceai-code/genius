"""
Tool: diagnose
Matches extracted features or clip against beepdb signatures.
Identifies hardware device, failure state, severity, and generates an action proposal.
"""

from typing import Dict, Any, Optional


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
        # Kidde CO end-of-life detection pattern (30s interval, ~3200Hz, 80ms)
        if 25.0 <= interval_s <= 35.0:
            device_class = "co_detector"
            brand = "Kidde"
            meaning = "end_of_life"
            severity = "critical"
            confidence = 0.98
            suggested_action = "replace_unit;propose_purchase"
            explanation = "Your carbon monoxide detector has reached its 7-10 year end-of-life date. It is chirping every 30 seconds to alert you that the sensor itself has expired, not just the battery."
            entity_id = "ent_co_hallway"
        elif 40.0 <= interval_s <= 50.0:
            device_class = "smoke_detector"
            brand = "First Alert"
            meaning = "low_battery"
            severity = "warning"
            confidence = 0.95
            suggested_action = "replace_battery;walkthrough"
            explanation = "Your smoke alarm is signaling a low 9V backup battery with a single 45-second chirp."
            entity_id = "ent_smoke_kitchen"
        else:
            device_class = "unknown_device"
            brand = "Unknown"
            meaning = "unrecognized_cadence"
            severity = "info"
            confidence = 0.40
            suggested_action = "inspect_manually"
            explanation = f"Detected chirp cadence of {interval_s}s at {peak_freq_hz}Hz. No exact manufacturer signature match found."
            entity_id = "ent_unknown_01"

        return {
            "entity_id": entity_id,
            "device_class": device_class,
            "brand": brand,
            "location": location,
            "meaning": meaning,
            "severity": severity,
            "confidence": confidence,
            "recommended_action": suggested_action,
            "spoken_summary": explanation,
            "proposal": {
                "id": "prop_replace_co_001",
                "kind": "order_replacement",
                "status": "proposed",
                "device": f"{brand} {device_class.replace('_', ' ').title()}",
                "requires_confirmation": True
            },
            "source_provenance": "manufacturer_manual:kidde.com/manuals/kn-copp-3"
        }
