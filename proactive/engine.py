"""
Proactive Intelligence Engine
Decides WHAT to say and WHEN by continuously evaluating the Home Graph state.
Pushes unprompted events across active transports (SSE to Device Simulator).
"""

import datetime
import uuid
import logging
from typing import Dict, Any, List, Optional

from graph.store import HomeGraphStore, GRAPH_STORE
from proactive.transports.sse import SSE_BROADCASTER

logger = logging.getLogger("genius.proactive.engine")


class ProactiveEngine:
    def __init__(self, store: HomeGraphStore = GRAPH_STORE):
        self.store = store

    def generate_delivery_followup(self, entity_id: str = "ent_co_hallway") -> Dict[str, Any]:
        """
        Rule 1: Post-Diagnosis Replacement Follow-up
        Fired when an ordered hardware replacement arrives at the home.
        """
        entity = self.store.get_entity(entity_id)
        brand = entity["brand"] if entity else "Kidde"
        loc = entity["location"] if entity else "hallway"
        
        event_id = f"evt_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        event = {
            "type": "genius.event",
            "event_id": event_id,
            "timestamp": now,
            "kind": "follow_up",
            "entity_id": entity_id,
            "title": "Replacement Delivery Arrived",
            "message": f"Your {brand} CO detector replacement arrived today. Is the {loc} unit still chirping?",
            "spoken_text": f"Your replacement carbon monoxide alarm just arrived on your front porch. Would you like me to walk you through replacing the {loc} unit?",
            "actions": [
                {"id": "walkthrough", "label": "Walk me through replacement"},
                {"id": "dismiss", "label": "Dismiss"}
            ]
        }
        return event

    def generate_freeze_risk_warning(self, outdoor_temp_f: float = 24.0) -> Optional[Dict[str, Any]]:
        """
        Rule 2: Environmental Freeze Risk
        Correlates impending sub-freezing temperatures with aging furnace/pipe infrastructure.
        """
        entities = self.store.list_entities(lifecycle_state="aging")
        furnace = next((e for e in entities if "furnace" in e["type"] or "hvac" in e["type"]), None)

        if not furnace or outdoor_temp_f > 32.0:
            return None

        event_id = f"evt_freeze_{uuid.uuid4().hex[:6]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "type": "genius.event",
            "event_id": event_id,
            "timestamp": now,
            "kind": "freeze_risk",
            "entity_id": furnace["id"],
            "title": "Freeze Warning · Aging Heating System",
            "message": f"Temperature dropping to {int(outdoor_temp_f)}°F tonight. Your {furnace['brand']} furnace is aging (manufactured 2015). Maintain thermostat at 68°F to prevent pipe freeze.",
            "spoken_text": f"A freeze alert is in effect with temperatures dropping to {int(outdoor_temp_f)} degrees. Because your basement furnace is aging, I recommend keeping your heat set to at least 68 degrees tonight.",
            "actions": [
                {"id": "set_temp_68", "label": "Set Thermostat to 68°F"},
                {"id": "dismiss", "label": "Acknowledge"}
            ]
        }

    async def emit_proactive_event(self, event: Dict[str, Any]):
        """Pushes event over SSE to all connected device simulator clients."""
        logger.info(f"Emitting proactive event: {event['title']} ({event['event_id']})")
        await SSE_BROADCASTER.broadcast(event)


# Singleton proactive engine
PROACTIVE_ENGINE = ProactiveEngine()
