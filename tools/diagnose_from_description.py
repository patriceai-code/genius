"""
Tool: diagnose_from_description
Voice-native diagnostic tool designed specifically for Alexa+ conversational flow.
Receives conversational parameters extracted by the Alexa+ model from the homeowner's speech:
- interval_s: Estimated seconds between chirps (e.g. 30s, 45s, 60s)
- chirps_per_burst: Number of chirps in each burst (1 = single chirp, 2 = double chirp, 3-5 = alarm pattern)
- brand: Brand visible or known to user (e.g. "Kidde", "First Alert", "Nest")
- location: Room location (e.g. "hallway", "kitchen", "basement")
- device_hint: User description (e.g. "smoke detector", "carbon monoxide", "fridge")
"""

from typing import Dict, Any, Optional, List
import logging
from audio.matcher import load_beepdb
from graph.store import GRAPH_STORE

logger = logging.getLogger("genius.tools.diagnose_from_description")


def match_description(
    interval_s: Optional[float] = None,
    chirps_per_burst: Optional[int] = 1,
    brand: Optional[str] = None,
    device_hint: Optional[str] = None,
    db_rows: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """Matches conversational cues against beepdb device profiles."""
    if db_rows is None:
        db_rows = load_beepdb()

    candidates = []
    target_interval = interval_s if interval_s is not None else 30.0

    for row in db_rows:
        score = 0.0
        row_interval = float(row.get("signature_interval_s", 60.0))
        row_brand = row.get("brand", "").lower()
        row_class = row.get("device_class", "").lower()
        row_burst = int(row.get("chirps_per_burst", 1))

        # 1. Interval matching (±15% tolerance)
        interval_diff = abs(row_interval - target_interval)
        if interval_diff <= 5.0:
            score += 0.50
        elif interval_diff <= 15.0:
            score += 0.25

        # 2. Brand matching
        if brand and brand.lower() in row_brand:
            score += 0.35

        # 3. Device class / hint matching
        if device_hint:
            hint_clean = device_hint.lower().replace(" ", "_")
            if hint_clean in row_class or row_class in hint_clean:
                score += 0.25

        # 4. Chirps per burst matching
        if chirps_per_burst is not None and chirps_per_burst == row_burst:
            score += 0.15

        if score >= 0.40:
            candidates.append((score, row))

    if not candidates:
        return None

    # Sort descending by score
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_row = candidates[0]
    best_row_copy = dict(best_row)
    best_row_copy["match_confidence"] = min(0.99, round(best_score, 2))
    return best_row_copy


def register_diagnose_from_description(server):
    @server.tool(
        name="diagnose_from_description",
        description="Voice-native diagnostic tool for Alexa+ conversational flow. Diagnoses an appliance malfunction from verbal cues (chirp interval, count per burst, brand, and room location) without requiring raw audio."
    )
    def diagnose_from_description(
        interval_s: Optional[float] = 30.0,
        chirps_per_burst: Optional[int] = 1,
        brand: Optional[str] = None,
        location: str = "hallway",
        device_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates conversational description, updates Home Graph, and stages remediation proposal.
        """
        match = match_description(
            interval_s=interval_s,
            chirps_per_burst=chirps_per_burst,
            brand=brand,
            device_hint=device_hint
        )

        if not match:
            return {
                "matched": False,
                "entity_id": "ent_unknown",
                "brand": brand or "Unknown",
                "location": location,
                "spoken_summary": "I couldn't identify the device from that description. Could you tell me roughly how many seconds are between the beeps, or whether there is a brand name on the unit?",
                "clarification_needed": ["interval_seconds", "brand_name"],
                "proposal": None
            }

        device_class = match.get("device_class", "appliance")
        matched_brand = match.get("brand", "Unknown")
        meaning = match.get("meaning", "malfunction")
        severity = match.get("severity", "warning")
        confidence = match.get("match_confidence", 0.85)
        source_url = match.get("source_url", "")
        action = match.get("action", "inspect")

        entity_id = f"ent_{device_class}_{location.lower()}"

        # 1. Update/Register Entity in Home Graph
        lifecycle_state = "end_of_life" if meaning == "end_of_life" else "healthy"
        GRAPH_STORE.upsert_entity(
            entity_id=entity_id,
            entity_type=device_class,
            brand=matched_brand,
            model="KN-COPP-3" if "Kidde" in matched_brand else "Standard",
            location=location,
            lifecycle_state=lifecycle_state,
            provenance=f"conversational_voice_description:interval={interval_s}s,burst={chirps_per_burst}",
            confidence=confidence
        )

        # 2. Record Incident
        incident = GRAPH_STORE.record_incident(
            entity_id=entity_id,
            diagnosis=f"{meaning} ({device_class})",
            evidence_ref=f"conversational_verbal_cues:interval={interval_s}s,burst={chirps_per_burst},brand={matched_brand}",
            severity=severity,
            confidence=confidence,
            provenance=f"manufacturer_manual:{source_url}"
        )

        # 3. Create Proposal only if match confidence is sufficient (>= 0.70)
        prop = None
        proposal_payload = {}
        proposal_title = ""
        if confidence >= 0.70:
            proposal_kind = "order_replacement" if meaning == "end_of_life" else "replace_battery"
            proposal_title = "Order Replacement Unit ($34.99)" if meaning == "end_of_life" else "Order 9V Batteries / Walkthrough"

            proposal_payload = {
                "title": proposal_title,
                "device": f"{matched_brand} {device_class.replace('_', ' ').title()}",
                "location": location,
                "action": action,
                "severity": severity,
                "estimated_cost_usd": 34.99 if meaning == "end_of_life" else 8.99,
                "simulated_shipping_partner": "Amazon Prime (Next-Day Delivery)"
            }

            import os
            prop = GRAPH_STORE.create_proposal(
                incident_id=incident["incident_id"],
                kind=proposal_kind,
                payload=proposal_payload,
                proposal_id=f"prop_{device_class}_{meaning[:8]}_{os.urandom(3).hex()}"
            )

        # Calibrated spoken diagnosis based on confidence
        if confidence >= 0.85:
            spoken_diagnosis = (
                f"Based on a chirp every {int(interval_s or 30)} seconds, that's your {location} {matched_brand} {device_class.replace('_', ' ')} "
                f"indicating {meaning.replace('_', ' ')}. "
            )
            if meaning == "end_of_life":
                spoken_diagnosis += "This means the chemical sensor has expired after its service lifetime—not a low battery. I have prepared a replacement order proposal for your review."
            else:
                spoken_diagnosis += "I have staged a replacement battery walkthrough and order proposal for your confirmation."
        elif confidence >= 0.70:
            spoken_diagnosis = (
                f"Based on a chirp every {int(interval_s or 30)} seconds, this is most consistent with a {matched_brand} {device_class.replace('_', ' ')} "
                f"indicating {meaning.replace('_', ' ')}. I have staged a candidate proposal for your review."
            )
        else:
            spoken_diagnosis = (
                f"I detected a possible pattern matching a {matched_brand} {device_class.replace('_', ' ')}, but my confidence is low at {int(confidence * 100)} percent. "
                f"Could you verify the brand name on the alarm faceplate or check how many seconds elapse between chirps?"
            )

        return {
            "matched": True,
            "entity_id": entity_id,
            "device_class": device_class,
            "brand": matched_brand,
            "location": location,
            "meaning": meaning,
            "severity": severity,
            "confidence": confidence,
            "source_citation": source_url,
            "spoken_summary": spoken_diagnosis,
            "proposal": {
                "proposal_id": prop["proposal_id"],
                "title": proposal_title,
                "cost_usd": proposal_payload["estimated_cost_usd"],
                "status": "staged_pending_user_confirmation"
            } if prop else None
        }
