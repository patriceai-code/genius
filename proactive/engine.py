"""
Proactive Intelligence Engine
Decides WHAT to say and WHEN by continuously evaluating the Home Graph state.
Pushes unprompted events across active transports (SSE to Device Simulator).
"""

import datetime
import uuid
import math
import logging
from typing import Dict, Any, List, Optional

from graph.store import HomeGraphStore, GRAPH_STORE
from proactive.transports.sse import SSE_BROADCASTER

logger = logging.getLogger("genius.proactive.engine")


def simulate_thermal_freeze_counterfactual(
    outdoor_temp_f: float = 24.0,
    initial_indoor_temp_f: float = 68.0,
    time_horizon_hours: int = 48,
    tau_building_hours: float = 28.0,
    tau_pipe_zone_hours: float = 16.0
) -> Dict[str, Any]:
    """
    Simulates residential building thermodynamics and freeze progression under two counterfactual branches:
    Branch A: Active Thermostat Maintenance (furnace operating normally at setpoint 68°F).
    Branch B: Aging Furnace Lockout (unheated exponential cooling towards ambient outdoor temp).

    Governing differential equation (Newton's cooling law / lumped thermal capacitance):
        dT_in / dt = - (1 / tau) * (T_in - T_out) + (Q_hvac / C_thermal)

    Unheated analytic solution:
        T_zone(t) = T_out + (T_zone(0) - T_out) * exp(-t / tau)
    """
    delta_t = initial_indoor_temp_f - outdoor_temp_f
    freeze_threshold = 32.0

    # Calculate time to reach freezing threshold (32°F) in unheated pipe zone
    if outdoor_temp_f < freeze_threshold and delta_t > 0:
        target_delta = freeze_threshold - outdoor_temp_f
        ratio = target_delta / delta_t
        time_to_freeze_pipe_zone = -tau_pipe_zone_hours * math.log(ratio) if ratio > 0 else 0.0
        time_to_freeze_building = -tau_building_hours * math.log(ratio) if ratio > 0 else 0.0
    else:
        time_to_freeze_pipe_zone = float("inf")
        time_to_freeze_building = float("inf")

    # Trajectory projection at discrete intervals
    trajectory = []
    for h in [0, 6, 12, 18, 24, 36, 48]:
        t_envelope = outdoor_temp_f + delta_t * math.exp(-h / tau_building_hours)
        t_pipe = outdoor_temp_f + delta_t * math.exp(-h / tau_pipe_zone_hours)
        trajectory.append({
            "elapsed_hours": h,
            "unheated_envelope_temp_f": round(t_envelope, 1),
            "unheated_pipe_zone_temp_f": round(t_pipe, 1),
            "maintained_setpoint_temp_f": initial_indoor_temp_f
        })

    pipe_freeze_risk_pct = 94.0 if time_to_freeze_pipe_zone <= time_horizon_hours else 15.0

    return {
        "physics_model": "lumped_capacitance_building_cooling",
        "outdoor_ambient_temp_f": outdoor_temp_f,
        "setpoint_target_temp_f": initial_indoor_temp_f,
        "envelope_time_constant_tau_hours": tau_building_hours,
        "pipe_zone_time_constant_tau_hours": tau_pipe_zone_hours,
        "time_to_pipe_freeze_hours": round(time_to_freeze_pipe_zone, 1),
        "counterfactual_analysis": {
            "branch_a_active_control": {
                "furnace_state": "active_monitoring",
                "minimum_predicted_pipe_temp_f": 52.0,
                "freeze_probability": 0.0,
                "status": "safe_nominal"
            },
            "branch_b_unmitigated_lockout": {
                "furnace_state": "filter_pressure_trip_lockout",
                "time_to_pipe_freeze_hours": round(time_to_freeze_pipe_zone, 1),
                "time_to_envelope_freeze_hours": round(time_to_freeze_building, 1),
                "freeze_probability": pipe_freeze_risk_pct / 100.0,
                "status": "critical_pipe_burst_risk"
            }
        },
        "cooling_trajectory": trajectory
    }


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
        Rule 2: Environmental Freeze Risk with Predictive Counterfactual Simulation
        Correlates impending sub-freezing temperatures with aging furnace/pipe infrastructure
        and runs a 48-hour thermodynamic trajectory simulation.
        """
        entities = self.store.list_entities(lifecycle_state="aging")
        furnace = next((e for e in entities if "furnace" in e["type"] or "hvac" in e["type"]), None)

        if not furnace or outdoor_temp_f > 32.0:
            return None

        event_id = f"evt_freeze_{uuid.uuid4().hex[:6]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        simulation = simulate_thermal_freeze_counterfactual(outdoor_temp_f=outdoor_temp_f)
        hours_to_freeze = simulation["time_to_pipe_freeze_hours"]

        return {
            "type": "genius.event",
            "event_id": event_id,
            "timestamp": now,
            "kind": "freeze_risk",
            "entity_id": furnace["id"],
            "title": "Freeze Warning · Aging Heating System",
            "message": f"Temperature dropping to {int(outdoor_temp_f)}°F tonight. Your {furnace['brand']} furnace is aging (manufactured 2015). Simulation projects pipe freeze risk within {hours_to_freeze}h if unmitigated. Maintain thermostat at 68°F.",
            "spoken_text": f"A freeze alert is in effect with temperatures dropping to {int(outdoor_temp_f)} degrees. Because your basement furnace is aging, I recommend keeping your heat set to at least 68 degrees tonight.",
            "simulation": simulation,
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
