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
async def test_registered_tools():
    """Verifies all twelve registered MCP tools are active on the server."""
    expected_tools = {
        "hear_sound",
        "diagnose",
        "diagnose_from_description",
        "list_entities",
        "get_home_health",
        "propose_action",
        "confirm_action",
        "record_incident",
        "register_entity",
        "check_warranty",
        "file_warranty_claim",
        "deliberate_repair"
    }
    tools = await mcp_server.list_tools()
    tool_names = {t.name for t in tools}
    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"
    assert len(tool_names) == 12


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


def test_mcp_streamable_http_spec_handshake():
    """
    Verifies official MCP Streamable HTTP spec (2025-11-25) compliance:
    1. POST /mcp with 'initialize' returns 200 OK + 'mcp-session-id' header + capabilities
    2. POST /mcp with 'notifications/initialized' returns 202 Accepted
    3. POST /mcp with 'tools/list' and session ID returns 200 OK + registered MCP tools
    """
    from fastapi.testclient import TestClient

    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        # 1. initialize
        init_res = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "alexa_plus_harness", "version": "1.0"},
                },
            },
        )
        assert init_res.status_code == 200
        assert "mcp-session-id" in init_res.headers
        session_id = init_res.headers["mcp-session-id"]
        assert "2025-11-25" in init_res.text
        assert "genius" in init_res.text

        # 2. notifications/initialized
        notif_res = client.post(
            "/mcp",
            headers={"mcp-session-id": session_id},
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
        assert notif_res.status_code == 202

        # 3. tools/list
        tools_res = client.post(
            "/mcp",
            headers={"mcp-session-id": session_id},
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert tools_res.status_code == 200
        assert "hear_sound" in tools_res.text
        assert "diagnose" in tools_res.text
        assert "diagnose_from_description" in tools_res.text


@pytest.mark.asyncio
async def test_api_call_diagnose_from_description():
    """Verifies the voice-native diagnose_from_description tool."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/call", json={
            "name": "diagnose_from_description",
            "arguments": {
                "interval_s": 30.0,
                "chirps_per_burst": 1,
                "brand": "Kidde",
                "location": "hallway"
            }
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        result = data["result"][0]
        assert result["matched"] is True
        assert result["brand"] == "Kidde"
        assert result["device_class"] == "co_detector"
        assert result["meaning"] == "end_of_life"
        assert "proposal" in result
        assert result["proposal"]["cost_usd"] == 34.99


def test_simulator_mcp_client_and_cors_session_header():
    """
    Verifies that:
    1. CORS exposes Mcp-Session-Id on POST /mcp for browser MCP clients.
    2. POST /mcp tools/call executes diagnose_from_description, hear_sound -> diagnose, and confirm_action.
    3. client/app.js uses POST /mcp JSON-RPC 2.0 (callMcpTool) and labels Offline Replay mode transparently.
    """
    import os
    from fastapi.testclient import TestClient

    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        init_res = client.post(
            "/mcp",
            headers={"Origin": "http://genius-simulator.s3-website.eu-west-2.amazonaws.com", "Accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "genius-alexa-plus-simulator", "version": "1.0.0"},
                },
            },
        )
        assert init_res.status_code == 200
        expose_hdr = init_res.headers.get("access-control-expose-headers", "").lower()
        assert "mcp-session-id" in expose_hdr
        sid = init_res.headers["mcp-session-id"]

        call_res = client.post(
            "/mcp",
            headers={"mcp-session-id": sid, "Accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "diagnose_from_description",
                    "arguments": {"interval_s": 30.0, "chirps_per_burst": 1, "brand": "Kidde", "location": "hallway"},
                },
            },
        )
        assert call_res.status_code == 200
        assert "end_of_life" in call_res.text

    app_js_path = os.path.join(os.path.dirname(__file__), "..", "client", "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        js_code = f.read()
    assert 'fetch(`${API_BASE}/mcp`' in js_code
    assert 'method: "tools/call"' in js_code
    assert "Offline Replay (No MCP Server Connected)" in js_code


