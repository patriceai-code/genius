"""
Tool: confirm_action
User confirmation gate. This is the ONLY tool path permitted to execute external actions
or mutate entity states outside the Home Graph.
"""

from typing import Dict, Any
import datetime


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
        Processes confirmed proposal.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if not confirmed:
            return {
                "proposal_id": proposal_id,
                "status": "dismissed",
                "executed": False,
                "timestamp": timestamp,
                "message": "Action was declined by the user. No changes were made."
            }

        return {
            "proposal_id": proposal_id,
            "status": "confirmed_and_executed",
            "executed": True,
            "timestamp": timestamp,
            "result": {
                "order_ref": "AMZN-2026-94819",
                "item": "Kidde Hardwired Carbon Monoxide Alarm with 10-Year Sealed Battery",
                "estimated_delivery": "Today by 6:00 PM",
                "tracking_status": "dispatched"
            },
            "message": "Action confirmed. Replacement unit dispatched. Tracking registered in Home Graph for proactive follow-up."
        }
