"""
Tool: propose_action
Creates an actionable proposal in the Home Graph.
ARCHITECTURAL RULE: Never auto-acts. All physical or external actions
must be proposed first and require explicit user confirmation.
"""

from typing import Dict, Any, Optional
from graph.store import GRAPH_STORE


def register_propose_action(server):
    @server.tool(
        name="propose_action",
        description="Creates an action proposal in the Home Graph. Architectural safety guarantee: This tool NEVER executes mutations externally; it only records a proposal awaiting user confirmation."
    )
    def propose_action(
        kind: str,
        title: str,
        description: str,
        payload: Dict[str, Any],
        incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers a proposed action in the persistent Home Graph.
        """
        enriched_payload = {**payload, "title": title, "description": description}
        proposal = GRAPH_STORE.create_proposal(
            incident_id=incident_id,
            kind=kind,
            payload=enriched_payload
        )

        return {
            "proposal_id": proposal["proposal_id"],
            "incident_id": incident_id,
            "kind": kind,
            "title": title,
            "description": description,
            "payload": payload,
            "status": "proposed",
            "created_at": proposal["created_at"],
            "requires_user_confirmation": True,
            "trust_policy": "never_auto_act_enforced"
        }
