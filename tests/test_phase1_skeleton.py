"""
Unit & Integration Test for Phase 1 Walking Skeleton
Verifies:
1. MCP Server initialization & loaded config
2. Registration of the seven core MCP tools
3. Tool execution via direct call
4. FastAPI endpoints (/api/config, /api/tools, /api/call)
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from server.main import app, mcp_server
from server.config import CONFIG


@pytest.mark.asyncio
async def test_mcp_config():
    """Verifies loaded MCP config matches hackathon submission requirements."""
    cfg = CONFIG.to_dict()
    assert cfg["server"]["name"] == "genius"
    assert cfg["server"]["mcp_spec"] == "2025-11-25"
    assert "/mcp" in cfg["transports"]["mcp_streamable_http"]
    assert "/events" in cfg["transports"]["sse_proactive_push"]


@pytest.mark.asyncio
async def test_registered_seven_tools():
    """Verifies all seven required MCP tools are registered."""
    expected_tools = {
        "hear_sound",
        "diagnose",
        "list_entities",
        "get_home_health",
        "propose_action",
        "confirm_action",
        "record_incident"
    }
    tools = await mcp_server.list_tools()
    tool_names = {t.name for t in tools}
    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"
    assert len(tool_names) >= 7


@pytest.mark.asyncio
async def test_api_tools_endpoint():
    """Verifies the /api/tools endpoint returns the tools for the simulator."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 7
        tool_names = [t["name"] for t in data["tools"]]
        assert "hear_sound" in tool_names
        assert "diagnose" in tool_names


@pytest.mark.asyncio
async def test_api_call_diagnose_and_confirm():
    """Verifies the diagnose -> propose -> confirm loop."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Diagnose chirp
        diag_res = await client.post("/api/call", json={
            "name": "diagnose",
            "arguments": {"interval_s": 30.0, "location": "hallway"}
        })
        assert diag_res.status_code == 200
        diag_data = diag_res.json()
        assert diag_data["status"] == "success"
        result_payload = diag_data["result"][0]
        assert result_payload["device_class"] == "co_detector"
        assert result_payload["meaning"] == "end_of_life"
        assert result_payload["confidence"] >= 0.95

        # 2. Confirm action
        conf_res = await client.post("/api/call", json={
            "name": "confirm_action",
            "arguments": {"proposal_id": result_payload["proposal"]["id"], "confirmed": True}
        })
        assert conf_res.status_code == 200
        conf_data = conf_res.json()
        assert conf_data["status"] == "success"
        conf_payload = conf_data["result"][0]
        assert conf_payload["executed"] is True
        assert "AMZN-2026-94819" in conf_payload["result"]["order_ref"]
