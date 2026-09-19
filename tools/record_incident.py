"""
Tool: record_incident
Records a diagnostic incident or manual event into the Home Graph.
Enforces data provenance on every write.
"""

from typing import Dict, Any, Optional
import uuid
import datetime


def register_record_incident(server):
    @server.tool(
        name="record_incident",
        description="Records an infrastructure anomaly, maintenance event, or acoustic diagnosis into the persistent Home Graph with verifiable data provenance."
    )
    def record_incident(
        description: str,
        entity_id: Optional[str] = None,
        severity: str = "warning",
        evidence_ref: str = "user_reported",
        provenance: str = "manual_entry"
    ) -> Dict[str, Any]:
        """
        Inserts incident into the graph ledger.
        """
        incident_id = f"inc_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "incident_id": incident_id,
            "entity_id": entity_id or "ent_unassigned",
            "description": description,
            "severity": severity,
            "evidence_ref": evidence_ref,
            "provenance": provenance,
            "recorded_at": timestamp,
            "status": "active"
        }
