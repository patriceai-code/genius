"""
Tool: propose_action
Creates an actionable proposal.
ARCHITECTURAL RULE: Never auto-acts. All physical or external actions
must be proposed first and require explicit user confirmation.
"""

from typing import Dict, Any, Optional
import uuid
import datetime


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
        Registers a proposed action in the graph.
        """
        proposal_id = f"prop_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "proposal_id": proposal_id,
            "incident_id": incident_id,
            "kind": kind,
            "title": title,
            "description": description,
            "payload": payload,
            "status": "proposed",
            "created_at": timestamp,
            "requires_user_confirmation": True,
            "trust_policy": "never_auto_act_enforced"
        }
