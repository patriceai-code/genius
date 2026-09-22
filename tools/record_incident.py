"""
Tool: record_incident
Records a diagnostic incident or manual event into the persistent Home Graph.
Enforces data provenance on every write.
"""

from typing import Dict, Any, Optional
from graph.store import GRAPH_STORE


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
        target_entity = entity_id or "ent_unassigned"
        incident = GRAPH_STORE.record_incident(
            entity_id=target_entity,
            diagnosis=description,
            evidence_ref=evidence_ref,
            severity=severity,
            confidence=1.0,
            provenance=provenance
        )

        return {
            "incident_id": incident["incident_id"],
            "entity_id": incident["entity_id"],
            "description": incident["diagnosis"],
            "severity": incident["severity"],
            "evidence_ref": incident["evidence_ref"],
            "provenance": incident["provenance"],
            "recorded_at": incident["created_at"],
            "status": "active"
        }
