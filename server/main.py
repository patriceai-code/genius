"""
GENIUS MCP Server Main Entry Point
Adheres to Model Context Protocol (MCP) 2025-11-25 Streamable HTTP Transport
Provides FastMCP server, SSE proactive push, and companion simulator API.
"""

from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.mcpserver import MCPServer

from server.config import CONFIG
from tools import register_all_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("genius.server")

# Instantiate MCPServer
mcp_server = MCPServer(CONFIG.server_name)
register_all_tools(mcp_server)

# In-memory SSE subscriber queues for the Device Simulator
proactive_subscribers = set()


async def broadcast_proactive_event(event_data: Dict[str, Any]):
    """Broadcasts a proactive event to all connected simulator clients via SSE."""
    dead_queues = set()
    payload = f"data: {json.dumps(event_data)}\n\n"
    for queue in list(proactive_subscribers):
        try:
            await queue.put(payload)
        except Exception:
            dead_queues.add(queue)
    for dead in dead_queues:
        proactive_subscribers.discard(dead)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GENIUS MCP Server...")
    logger.info("MCP Streamable HTTP transport configured at %s", CONFIG.streamable_path)
    logger.info("SSE Proactive Events channel configured at %s", CONFIG.sse_events_path)
    yield
    logger.info("Shutting down GENIUS MCP Server...")


# Master FastAPI application
app = FastAPI(
    title=CONFIG.server_title,
    version=CONFIG.server_version,
    lifespan=lifespan,
    description="GENIUS MCP Server with Streamable HTTP & SSE Push for Alexa+ Developer Hackathon"
)

# CORS middleware for local web client testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP Streamable HTTP Application under /mcp
mcp_app = mcp_server.streamable_http_app(streamable_http_path=CONFIG.streamable_path)
app.mount("/mcp", mcp_app)


# REST / Inspection Endpoints for Hackathon Judges & Device Simulator

@app.get("/api/config")
async def get_mcp_config():
    """Returns loaded MCP configuration (Submission Requirement: inspectable in code/API)."""
    return JSONResponse(CONFIG.to_dict())


@app.get("/api/tools")
async def list_registered_tools():
    """Lists all 7 registered MCP tools and their parameter schemas."""
    tools = await mcp_server.list_tools()
    tool_list = []
    for t in tools:
        tool_list.append({
            "name": t.name,
            "description": t.description,
            "inputSchema": getattr(t, "inputSchema", {})
        })
    return JSONResponse({
        "mcp_spec": CONFIG.mcp_spec_version,
        "count": len(tool_list),
        "tools": tool_list
    })


@app.post("/api/call")
async def call_tool_direct(request: Request):
    """Direct JSON caller for the Device Simulator UI to invoke any registered MCP tool."""
    body = await request.json()
    tool_name = body.get("name")
    arguments = body.get("arguments", {})
    try:
        result = await mcp_server.call_tool(tool_name, arguments)
        # Extract content from CallToolResult
        formatted_content = []
        for item in getattr(result, "content", []):
            if hasattr(item, "text"):
                try:
                    formatted_content.append(json.loads(item.text))
                except Exception:
                    formatted_content.append(item.text)
            else:
                formatted_content.append(str(item))
        return JSONResponse({"status": "success", "result": formatted_content})
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return JSONResponse({"status": "error", "error": str(e)}, status_code=400)


# SSE Proactive Push Endpoint for Alexa+ Simulator

@app.get("/events")
async def sse_event_stream(request: Request):
    """Server-Sent Events endpoint pushing unprompted home notifications to the tablet client."""
    queue: asyncio.Queue = asyncio.Queue()
    proactive_subscribers.add(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Initial handshake event
            yield f"data: {json.dumps({'type': 'genius.connected', 'message': 'GENIUS Proactive SSE Channel Active', 'timestamp': 'now'})}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield data
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield ": ping\n\n"
        finally:
            proactive_subscribers.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Demo Flow Triggers for Testing & Walkthrough

@app.post("/simulate/chirp")
async def trigger_chirp_simulation(request: Request):
    """Simulates 3:14 AM acoustic chirp detection and runs diagnose tool."""
    body = await request.json() if await request.body() else {}
    interval = body.get("interval_s", 30.0)
    res = await mcp_server.call_tool("diagnose", {"interval_s": interval, "location": "hallway"})
    
    # Broadcast incident detection event
    event = {
        "type": "genius.event",
        "kind": "acoustic_incident",
        "title": "Acoustic Anomaly Detected",
        "message": "Hallway Carbon Monoxide detector chirping every 30s. Sensor end-of-life reached.",
        "severity": "critical",
        "entity_id": "ent_co_hallway",
        "proposal_id": "prop_replace_co_001",
        "actions": [
            {"id": "confirm", "label": "Order Replacement ($34.99)"},
            {"id": "dismiss", "label": "Dismiss"}
        ]
    }
    await broadcast_proactive_event(event)
    return JSONResponse({"status": "simulated", "tool_result": [c.text for c in getattr(res, "content", [])]})


@app.post("/simulate/delivery")
async def trigger_delivery_followup():
    """Simulates proactive delivery arrival: 'Your CO detector arrived today. Still chirping?'"""
    event = {
        "type": "genius.event",
        "event_id": "evt_delivery_followup_001",
        "kind": "proactive_follow_up",
        "title": "Delivery Arrived",
        "message": "Your Kidde CO detector replacement arrived today. Is the hallway unit still chirping?",
        "spoken_text": "Your replacement carbon monoxide alarm just arrived on your porch. Would you like me to walk you through replacing the hallway unit?",
        "entity_id": "ent_co_hallway",
        "actions": [
            {"id": "walkthrough", "label": "Walk me through replacement"},
            {"id": "resolved", "label": "All sorted, thanks"}
        ]
    }
    await broadcast_proactive_event(event)
    return JSONResponse({"status": "event_broadcast", "event": event})


# Mount Static Files for Client Simulator
app.mount("/client", StaticFiles(directory="client", html=True), name="client")


@app.get("/")
async def root_redirect():
    """Redirects root to the device simulator UI."""
    return HTMLResponse("""
    <html>
        <head><meta http-equiv="refresh" content="0; url=/client/index.html" /></head>
        <body><p>Redirecting to <a href="/client/index.html">GENIUS Device Simulator</a>...</p></body>
    </html>
    """)
