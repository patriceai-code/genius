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
import numpy as np

from graph.store import HomeGraphStore, GRAPH_STORE
from proactive.transports.sse import SSE_BROADCASTER

logger = logging.getLogger("genius.proactive.engine")


def compute_freeze_monte_carlo(
    outdoor_temp_f: float = 24.0,
    initial_indoor_temp_f: float = 68.0,
    time_horizon_hours: int = 48,
    nominal_tau_pipe_hours: float = 16.0,
    n_simulations: int = 5000,
    seed: int = 0
) -> Dict[str, float]:
    """
    Computes empirical pipe freeze probability via Monte Carlo integration
    over parameter uncertainty (stochastic weather forecast error and building thermal variation).
    
    Model parameters:
        tau_pipe ~ Lognormal(ln(nominal_tau), sigma=0.3)
        T_out ~ Normal(outdoor_temp_f, sigma=2.5°F)
        T_in0 ~ Normal(initial_indoor_temp_f, sigma=2.0°F)
    """
    rng = np.random.default_rng(seed)
    tau = rng.lognormal(np.log(nominal_tau_pipe_hours), 0.3, n_simulations)
    t_out = rng.normal(outdoor_temp_f, 2.5, n_simulations)
    t_in0 = rng.normal(initial_indoor_temp_f, 2.0, n_simulations)
    
    # 48-hour time grid (0.1h steps)
    t = np.linspace(0, time_horizon_hours, int(time_horizon_hours * 10) + 1)[:, None]
    
    # Analytical trajectory array [time_steps, n_simulations]
    t_trajectories = t_out + (t_in0 - t_out) * np.exp(-t / tau)
    
    min_temps = t_trajectories.min(axis=0)
    p_freeze = float((min_temps <= 32.0).mean())
    median_time_to_freeze = float("inf")
    
    frozen_mask = (min_temps <= 32.0)
    if frozen_mask.any():
        # First time index where temperature drops below 32°F
        freeze_indices = np.argmax(t_trajectories[:, frozen_mask] <= 32.0, axis=0)
        freeze_times = t[freeze_indices, 0]
        median_time_to_freeze = float(np.median(freeze_times))
        
    return {
        "p_freeze_48h_pct": round(p_freeze * 100.0, 1),
        "median_time_to_freeze_hours": round(median_time_to_freeze, 1) if median_time_to_freeze != float("inf") else 0.0,
        "n_simulations": n_simulations
    }


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
        
    For an unheated pipe zone (e.g. crawlspace / exterior wall cavity, tau ≈ 16h) starting at 68°F 
    cooling towards 24°F:
        t_freeze = -16 * ln((32 - 24) / (68 - 24)) = -16 * ln(8/44) = 27.3 hours.
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

    # Run stochastic Monte Carlo simulation over forecast and thermal uncertainty
    mc_results = compute_freeze_monte_carlo(
        outdoor_temp_f=outdoor_temp_f,
        initial_indoor_temp_f=initial_indoor_temp_f,
        time_horizon_hours=time_horizon_hours,
        nominal_tau_pipe_hours=tau_pipe_zone_hours
    )
    pipe_freeze_risk_pct = mc_results["p_freeze_48h_pct"]

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

    return {
        "physics_model": "lumped_capacitance_building_cooling",
        "outdoor_ambient_temp_f": outdoor_temp_f,
        "setpoint_target_temp_f": initial_indoor_temp_f,
        "envelope_time_constant_tau_hours": tau_building_hours,
        "pipe_zone_time_constant_tau_hours": tau_pipe_zone_hours,
        "time_to_pipe_freeze_hours": round(time_to_freeze_pipe_zone, 1),
        "monte_carlo_validation": mc_results,
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
