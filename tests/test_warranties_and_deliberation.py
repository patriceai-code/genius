"""
Tests for Warranties, Device Onboarding, and Specialist Deliberation
"""

import pytest
from mcp.server.mcpserver import MCPServer
from graph.store import HomeGraphStore
from tools.register_entity import register_register_entity
from tools.check_warranty import register_check_warranty
from tools.file_warranty_claim import register_file_warranty_claim
from tools.deliberate_repair import register_deliberate_repair


@pytest.mark.asyncio
async def test_device_registration_and_warranty_tracking(tmp_path):
    """Verifies Day 0 device registration creates entity and warranty."""
    test_db = str(tmp_path / "test_warranties.db")
    store = HomeGraphStore(db_path=test_db)

    import graph.store
    import tools.register_entity
    import tools.check_warranty
    import tools.file_warranty_claim

    tools.register_entity.GRAPH_STORE = store
    tools.check_warranty.GRAPH_STORE = store
    tools.file_warranty_claim.GRAPH_STORE = store

    server = MCPServer("test_genius_warranties")
    register_register_entity(server)
    register_check_warranty(server)
    register_file_warranty_claim(server)

    # 1. Register a new 2024 Kidde Smoke Detector
    reg_res = await server.call_tool("register_entity", {
        "entity_type": "smoke_detector",
        "brand": "Kidde",
        "model": "P4010ACLEDS-2",
        "location": "hallway_upstairs",
        "manufacture_year": 2024,
        "warranty_years": 10
    })
    reg_text = [c.text for c in getattr(reg_res, "content", [])][0]
    assert "ent_smoke_detector_hallway_upstairs" in reg_text
    assert "healthy" in reg_text

    # 2. Check warranty
    check_res = await server.call_tool("check_warranty", {
        "entity_id": "ent_smoke_detector_hallway_upstairs"
    })
    check_text = [c.text for c in getattr(check_res, "content", [])][0]
    assert "Active & Covered" in check_text
    assert "2034-01-01" in check_text

    # 3. File warranty claim
    claim_res = await server.call_tool("file_warranty_claim", {
        "entity_id": "ent_smoke_detector_hallway_upstairs",
        "reason": "Chirping every 30s within warranty"
    })
    claim_text = [c.text for c in getattr(claim_res, "content", [])][0]
    assert "claim_proposed" in claim_text
    assert "prop_warranty_" in claim_text


@pytest.mark.asyncio
async def test_specialist_deliberation_repair_vs_replace(tmp_path):
    """Verifies AWS Builder Specialist Deliberation panel calculations."""
    test_db = str(tmp_path / "test_deliberation.db")
    store = HomeGraphStore(db_path=test_db)

    # Register an 11-year-old furnace
    store.upsert_entity(
        entity_id="ent_furnace_basement",
        entity_type="hvac_furnace",
        brand="Carrier",
        model="Infinity 98",
        location="basement",
        lifecycle_state="aging",
        provenance="photo_inspection:tag_scan"
    )

    import tools.deliberate_repair
    tools.deliberate_repair.GRAPH_STORE = store

    server = MCPServer("test_deliberation")
    register_deliberate_repair(server)

    delib_res = await server.call_tool("deliberate_repair", {
        "entity_id": "ent_furnace_basement"
    })
    delib_text = [c.text for c in getattr(delib_res, "content", [])][0]
    assert "REPLACE" in delib_text
    assert "financial_breakdown" in delib_text
    assert "annual_efficiency_savings" in delib_text
    assert "model_used" in delib_text
    assert "execution_mode" in delib_text


