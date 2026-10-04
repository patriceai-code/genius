"""
Unit & Integration Tests for GENIUS World-Model Physics:
1. Continuous Weibull Reliability & Degradation Hazard Modeling (BioSync/CAIN-style)
2. Predictive Lumped-Capacitance Building Freeze Counterfactual Simulation
3. Robust LLM JSON Parsing with Preambles/Fences
4. Home Health Continuous Fleet Scorecard Integration
"""

import pytest
import math
from graph.store import HomeGraphStore, calculate_continuous_reliability
from proactive.engine import simulate_thermal_freeze_counterfactual
from tools.utils import parse_json_from_llm


def test_weibull_continuous_reliability_calculation():
    """Verifies continuous Weibull reliability distributions across hardware types."""
    # 1. 7-year-old CO detector at its characteristic lifespan eta=7.0
    # Theoretical R(eta) = exp(-(1)^3.0) = exp(-1) = 0.3679
    rel_co_7yr = calculate_continuous_reliability("co_detector", age_years=7.0)
    assert abs(rel_co_7yr["reliability_rt"] - 0.3679) < 0.01
    assert rel_co_7yr["degradation_index"] > 0.60
    assert rel_co_7yr["weibull_shape_beta"] == 3.0

    # 2. Brand new 1-year-old smoke detector (eta=10, beta=2.5)
    rel_smoke_1yr = calculate_continuous_reliability("smoke_detector", age_years=1.0)
    assert rel_smoke_1yr["reliability_rt"] > 0.98
    assert rel_smoke_1yr["degradation_index"] < 0.02

    # 3. 11-year-old furnace (eta=15, beta=2.2)
    rel_furnace = calculate_continuous_reliability("hvac_furnace", age_years=11.0)
    assert 0.40 < rel_furnace["reliability_rt"] < 0.65
    assert rel_furnace["remaining_useful_life_years"] >= 0.0

    # 4. Monotonic hazard rate verification: hazard increases with wear-out (beta > 1)
    h_young = calculate_continuous_reliability("hvac_furnace", age_years=2.0)["hazard_rate"]
    h_old = calculate_continuous_reliability("hvac_furnace", age_years=12.0)["hazard_rate"]
    assert h_old > h_young, "Weibull hazard rate must increase monotonically for mechanical wear-out"


def test_thermal_freeze_counterfactual_simulation():
    """Verifies building lumped-capacitance thermodynamics and freeze projection."""
    # At 24°F ambient and 68°F indoor setpoint
    sim = simulate_thermal_freeze_counterfactual(outdoor_temp_f=24.0, initial_indoor_temp_f=68.0)

    assert sim["physics_model"] == "lumped_capacitance_building_cooling"
    assert sim["outdoor_ambient_temp_f"] == 24.0
    assert sim["setpoint_target_temp_f"] == 68.0

    # Theoretical time to freeze in unheated pipe zone (tau=16h):
    # delta_t = 68 - 24 = 44. target_delta = 32 - 24 = 8.
    # ratio = 8/44 = 0.1818. t = -16 * ln(0.1818) = 27.27 hours (approx 27.3h)
    assert 15.0 < sim["time_to_pipe_freeze_hours"] < 35.0

    # Branch A: active heating maintain safety
    branch_a = sim["counterfactual_analysis"]["branch_a_active_control"]
    assert branch_a["freeze_probability"] == 0.0
    assert branch_a["status"] == "safe_nominal"

    # Branch B: unmitigated lockout results in high freeze probability
    branch_b = sim["counterfactual_analysis"]["branch_b_unmitigated_lockout"]
    assert branch_b["freeze_probability"] >= 0.90
    assert branch_b["status"] == "critical_pipe_burst_risk"

    # Check cooling trajectory progression
    trajectory = sim["cooling_trajectory"]
    assert len(trajectory) == 7
    assert trajectory[0]["unheated_pipe_zone_temp_f"] == 68.0
    assert trajectory[-1]["unheated_pipe_zone_temp_f"] < 30.0


def test_parse_json_from_llm():
    """Verifies robust extraction of JSON across varied LLM output formats."""
    # 1. Fenced markdown block
    fenced = "```json\n{\"verdict\": \"REPLACE\", \"confidence\": 0.95}\n```"
    res1 = parse_json_from_llm(fenced)
    assert res1["verdict"] == "REPLACE"
    assert res1["confidence"] == 0.95

    # 2. Conversational preamble & postamble
    conversational = (
        "Here is my certified engineering deliberation:\n\n"
        "```\n{\"verdict\": \"REPAIR\", \"repair_cost\": 350}\n```\n\n"
        "Let me know if you would like to proceed with the repair."
    )
    res2 = parse_json_from_llm(conversational)
    assert res2["verdict"] == "REPAIR"
    assert res2["repair_cost"] == 350

    # 3. Direct raw JSON string with curly braces
    raw = "Deliberation result: {\"status\": \"ok\", \"payback_years\": 3.4}"
    res3 = parse_json_from_llm(raw)
    assert res3["status"] == "ok"
    assert res3["payback_years"] == 3.4


def test_home_health_continuous_fleet_metrics(tmp_path):
    """Verifies that Home Graph scorecard exposes continuous Weibull fleet reliability."""
    db_file = str(tmp_path / "test_reliability_graph.db")
    store = HomeGraphStore(db_path=db_file)

    health = store.get_home_health()
    assert "continuous_reliability" in health
    rel_meta = health["continuous_reliability"]

    assert 0.0 < rel_meta["fleet_survival_probability"] <= 1.0
    assert 0.0 <= rel_meta["mean_degradation_index"] < 1.0
    assert 0.0 < rel_meta["fleet_reliability_pct"] <= 100.0
    assert rel_meta["reliability_model"] == "weibull_hazard_continuous"
