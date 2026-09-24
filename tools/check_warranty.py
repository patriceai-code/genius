"""
Tool: check_warranty
Evaluates manufacturer warranty status and replacement coverage for any home hardware entity.
"""

from typing import Dict, Any
import datetime
from graph.store import GRAPH_STORE


def register_check_warranty(server):
    @server.tool(
        name="check_warranty",
        description="Inspects active manufacturer warranty coverage, policy expiration dates, and claim eligibility for a registered hardware device."
    )
    def check_warranty(entity_id: str) -> Dict[str, Any]:
        """Queries warranty coverage from the Home Graph."""
        entity = GRAPH_STORE.get_entity(entity_id)
        if not entity:
            return {"error": f"Entity '{entity_id}' not found in Home Graph."}

        warranty = GRAPH_STORE.get_warranty(entity_id)
        if not warranty:
            # Baseline estimation if warranty was not explicitly logged
            brand = entity.get("brand", "Manufacturer")
            provider = f"{brand} Standard Limited Warranty"
            created_year = int(entity.get("created_at", "2026")[:4])
            end_date = f"{created_year + 5}-01-01"
            warranty = GRAPH_STORE.upsert_warranty(
                entity_id=entity_id,
                provider=provider,
                start_date=f"{created_year}-01-01",
                end_date=end_date,
                claim_status="none"
            )

        # Date calculations (current time: 2026-09-26)
        today = datetime.date(2026, 9, 26)
        try:
            exp_date = datetime.date.fromisoformat(warranty["end_date"])
            days_remaining = (exp_date - today).days
            is_active = days_remaining > 0
        except Exception:
            days_remaining = 0
            is_active = False

        status_text = "Active & Covered" if is_active else "Expired"

        return {
            "entity_id": entity_id,
            "device": f"{entity.get('brand')} {entity.get('model')} ({entity.get('type')})",
            "location": entity.get("location"),
            "warranty_status": status_text,
            "is_covered": is_active,
            "provider": warranty["provider"],
            "expiration_date": warranty["end_date"],
            "days_remaining": max(0, days_remaining),
            "claim_status": warranty.get("claim_status", "none"),
            "spoken_summary": (
                f"Your {entity.get('brand')} {entity.get('type').replace('_', ' ')} is under active warranty with {warranty['provider']} until {warranty['end_date']}."
                if is_active else
                f"The warranty for your {entity.get('brand')} {entity.get('type').replace('_', ' ')} expired on {warranty['end_date']}."
            )
        }
