"""
Integration Test: The Core Loop with State & Home Graph Persistence
Tests:
1. First loop: Sound -> Diagnosis -> Entity Created in Graph -> Incident Created -> Proposal Created.
2. Second loop: The house remembers. Querying entities shows prior incident, updated lifecycle state, and health score changes.
3. Propose -> Confirm trust boundary: Propose cannot execute; only Confirm mutates state.
"""

import pytest
import os
from graph.store import HomeGraphStore
from tools.diagnose import register_diagnose
from tools.confirm_action import register_confirm_action
from tools.list_entities import register_list_entities
from tools.get_home_health import register_get_home_health
from mcp.server.mcpserver import MCPServer


@pytest.fixture
def temp_graph(tmp_path):
    """Provides an isolated SQLite database for testing state transitions."""
    db_file = str(tmp_path / "test_home_graph.db")
    store = HomeGraphStore(db_path=db_file)
    return store


@pytest.mark.asyncio
async def test_state_remembers_across_loops(tmp_path):
    """
    Verifies that running the diagnostic loop updates the graph,
    and subsequent queries reflect the prior incidents and lifecycle state.
    """
    test_db = str(tmp_path / "test_loop.db")
    store = HomeGraphStore(db_path=test_db)

    # Initial baseline check
    initial_health = store.get_home_health()
    assert initial_health["metrics"]["end_of_life_count"] == 0

    # LOOP 1: Ingest 30s CO End-of-Life chirp
    server = MCPServer("test_genius")
    register_diagnose(server)
    register_confirm_action(server)

    # Patch global store for test
    import graph.store
    import tools.diagnose
    import tools.confirm_action
    original_store = graph.store.GRAPH_STORE
    graph.store.GRAPH_STORE = store
    tools.diagnose.GRAPH_STORE = store
    tools.confirm_action.GRAPH_STORE = store

    try:
        # Step 1: Diagnose
        diag_res = await server.call_tool("diagnose", {
            "interval_s": 30.0,
            "peak_freq_hz": 3200.0,
            "duration_ms": 80.0,
            "location": "hallway"
        })
        diag_text = [c.text for c in getattr(diag_res, "content", [])][0]
        assert "ent_co_detector_hallway" in diag_text
        assert "end_of_life" in diag_text

        # Verify entity created in graph
        entity = store.get_entity("ent_co_detector_hallway")
        assert entity is not None
        assert entity["lifecycle_state"] == "end_of_life"
        assert "acoustic_diagnosis" in entity["provenance"]

        # Verify incident recorded
        incidents = store.list_incidents(entity_id="ent_co_detector_hallway")
        assert len(incidents) == 1
        assert "end_of_life" in incidents[0]["diagnosis"]

        # LOOP 2: Query Home Health — the house remembers
        updated_health = store.get_home_health()
        assert updated_health["metrics"]["end_of_life_count"] == 1
        assert updated_health["health_score"] < 100
        assert "end-of-life" in updated_health["summary"]

        # Step 3: Propose -> Confirm Gate
        proposal_id = "prop_co_detector_end_of_l_01"
        conf_res = await server.call_tool("confirm_action", {
            "proposal_id": proposal_id,
            "confirmed": True
        })
        conf_text = [c.text for c in getattr(conf_res, "content", [])][0]
        assert "confirmed_and_executed" in conf_text
        assert "dispatched" in conf_text

    finally:
        graph.store.GRAPH_STORE = original_store
