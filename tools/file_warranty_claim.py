"""
Tool: file_warranty_claim
Initiates a structured warranty replacement claim.
Follows strict Propose -> Confirm safety model: generates a claim proposal awaiting user approval.
"""

from typing import Dict, Any, Optional
import uuid
import datetime
from graph.store import GRAPH_STORE


def register_file_warranty_claim(server):
    @server.tool(
        name="file_warranty_claim",
        description="Prepares a manufacturer warranty claim dossier for an in-warranty failed device. Generates an actionable proposal awaiting explicit user confirmation."
    )
    def file_warranty_claim(
        entity_id: str,
        incident_id: Optional[str] = None,
        reason: str = "Hardware sensor expiration / defect"
    ) -> Dict[str, Any]:
        """Creates a warranty claim proposal."""
        entity = GRAPH_STORE.get_entity(entity_id)
        if not entity:
            return {"error": f"Entity '{entity_id}' not found in Home Graph."}

        warranty = GRAPH_STORE.get_warranty(entity_id)
        provider = warranty["provider"] if warranty else f"{entity.get('brand')} Warranty"

        claim_id = f"clm_{uuid.uuid4().hex[:6]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        proposal_payload = {
            "claim_id": claim_id,
            "entity_id": entity_id,
            "device": f"{entity.get('brand')} {entity.get('model')}",
            "location": entity.get("location"),
            "provider": provider,
            "reason": reason,
            "provenance_evidence": entity.get("provenance", "user_verified"),
            "claim_type": "free_manufacturer_replacement"
        }

        # Create proposal in Home Graph
        prop = GRAPH_STORE.create_proposal(
            incident_id=incident_id,
            kind="submit_warranty_claim",
            payload=proposal_payload,
            proposal_id=f"prop_warranty_{claim_id}"
        )

        # Update warranty claim status
        GRAPH_STORE.update_warranty_claim(entity_id, claim_status="claim_proposed")

        return {
            "status": "claim_proposed",
            "claim_id": claim_id,
            "entity_id": entity_id,
            "provider": provider,
            "proposal": {
                "id": prop["proposal_id"],
                "status": "proposed",
                "title": f"Submit Free Warranty Claim to {provider}",
                "requires_confirmation": True
            },
            "spoken_summary": f"I have prepared a warranty claim with {provider} for your {entity.get('brand')} {entity.get('type').replace('_', ' ')}. Would you like me to submit it for a free replacement?"
        }
