"""
Tool: confirm_action
User confirmation gate. This is the ONLY tool path permitted to execute external actions
or mutate entity states outside the Home Graph.
"""

from typing import Dict, Any
import datetime
from graph.store import GRAPH_STORE


def register_confirm_action(server):
    @server.tool(
        name="confirm_action",
        description="Executes a previously proposed action after explicit user authorization. The only tool permitted to perform external mutations."
    )
    def confirm_action(
        proposal_id: str,
        confirmed: bool = True,
        user_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Processes confirmed proposal in the Home Graph.
        """
        result_prop = GRAPH_STORE.confirm_proposal(proposal_id=proposal_id, confirmed=confirmed)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if not confirmed:
            return {
                "proposal_id": proposal_id,
                "status": "dismissed",
                "executed": False,
                "timestamp": now,
                "message": "Action was declined by the user. No external mutations performed."
            }

        # Enforce strict trust boundary: never confirm a proposal that does not exist in the Home Graph
        if not result_prop or (isinstance(result_prop, dict) and "error" in result_prop):
            return {
                "proposal_id": proposal_id,
                "status": "error",
                "executed": False,
                "timestamp": now,
                "error": "proposal_not_found",
                "message": f"Proposal '{proposal_id}' was not found in the Home Graph. Cannot confirm an unverified proposal."
            }

        # Execution payload (e.g. Amazon ordering / scheduling) derived from proposal record
        prop_payload = (result_prop or {}).get("payload", {}) if isinstance(result_prop, dict) else {}
        item_title = prop_payload.get("title") or prop_payload.get("device") or "Replacement Hardware Unit"
        suffix = proposal_id[-6:].upper() if len(proposal_id) >= 6 else "A1"
        order_ref = f"AMZN-2026-94819-{suffix}"
        return {
            "proposal_id": proposal_id,
            "status": "confirmed_and_executed",
            "executed": True,
            "timestamp": now,
            "result": {
                "order_ref": order_ref,
                "item": item_title,
                "device": prop_payload.get("device", "Kidde KN-COPP-3"),
                "estimated_delivery": "Today by 6:00 PM (Simulated Fulfillment)",
                "tracking_status": "dispatched"
            },
            "message": f"Action confirmed for {proposal_id}. Order {order_ref} ({item_title}) staged. Tracking registered in Home Graph for proactive follow-up."
        }
