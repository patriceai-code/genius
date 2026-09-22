"""
Tool: diagnose
Matches extracted features or clip against beepdb signatures.
Identifies hardware device, failure state, severity, and automatically
records the entity, incident, and proposal into the Home Graph.
"""

from typing import Dict, Any, Optional
import os

from audio.matcher import match_acoustic_features
from graph.store import GRAPH_STORE


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
        Evaluates acoustic signatures, updates the persistent Home Graph,
        and generates an action proposal.
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

        # 1. Update/Register Entity in Home Graph
        lifecycle_state = "end_of_life" if match.meaning == "end_of_life" else "healthy"
        GRAPH_STORE.upsert_entity(
            entity_id=entity_id,
            entity_type=match.device_class,
            brand=match.brand,
            model="KN-COPP-3" if "Kidde" in match.brand else "Standard",
            location=location,
            lifecycle_state=lifecycle_state,
            provenance=f"acoustic_diagnosis:{clip_id or 'live_audio'}",
            confidence=match.confidence
        )

        # 2. Record Incident in Home Graph
        incident = GRAPH_STORE.record_incident(
            entity_id=entity_id,
            diagnosis=f"{match.meaning} ({match.device_class})",
            evidence_ref=f"interval={interval_s}s,freq={peak_freq_hz}Hz,dur={duration_ms}ms",
            severity=match.severity,
            confidence=match.confidence,
            provenance=f"manufacturer_manual:{match.source_url}"
        )

        # 3. Create Proposal in Home Graph (Strict Propose -> Confirm Model)
        proposal_kind = "order_replacement" if match.meaning == "end_of_life" else "replace_battery"
        proposal_title = "Order Replacement Unit ($34.99)" if match.meaning == "end_of_life" else "Order 9V Batteries / Walkthrough"

        proposal_payload = {
            "title": proposal_title,
            "device": f"{match.brand} {match.device_class.replace('_', ' ').title()}",
            "location": location,
            "action": match.action,
            "incident_id": incident["incident_id"]
        }

        prop = GRAPH_STORE.create_proposal(
            incident_id=incident["incident_id"],
            kind=proposal_kind,
            payload=proposal_payload,
            proposal_id=f"prop_{match.device_class}_{match.meaning[:8]}_{os.urandom(3).hex()}"
        )

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
            "incident_id": incident["incident_id"],
            "proposal": {
                "id": prop["proposal_id"],
                "kind": prop["kind"],
                "status": prop["status"],
                "title": proposal_title,
                "requires_confirmation": True
            },
            "source_provenance": f"manufacturer_manual:{match.source_url}",
            "expected_specs": match_dict["expected_specs"]
        }
