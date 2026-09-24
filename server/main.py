"""
GENIUS MCP Server Main Entry Point
Adheres to Model Context Protocol (MCP) 2025-11-25 Streamable HTTP Transport
Provides FastMCP server, SSE proactive push, and companion simulator API.
"""

from contextlib import asynccontextmanager
import asyncio
import json
import logging
import uuid
import datetime
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


from graph.store import GRAPH_STORE
from audio.tts import synthesize_speech
from fastapi.responses import Response


@app.get("/api/warranties")
async def get_all_warranties():
    """Returns all active and expired warranties from the Home Graph."""
    warranties = GRAPH_STORE.list_warranties()
    return JSONResponse({"count": len(warranties), "warranties": warranties})


@app.get("/api/polly/speak")
async def polly_speak_get(text: str = ""):
    """Streams Polly neural audio for the given text."""
    if not text:
        return JSONResponse({"status": "error", "message": "No text provided"}, status_code=400)
    audio_bytes = synthesize_speech(text)
    if audio_bytes:
        return Response(content=audio_bytes, media_type="audio/mpeg")
    return JSONResponse({"status": "unavailable"}, status_code=404)


from proactive.transports.sse import SSE_BROADCASTER
from proactive.engine import PROACTIVE_ENGINE



# SSE Proactive Push Endpoint for Alexa+ Simulator

@app.get("/events")
async def sse_event_stream(request: Request):
    """Server-Sent Events endpoint pushing unprompted home notifications to the tablet client."""
    queue = SSE_BROADCASTER.subscribe()
    return StreamingResponse(
        SSE_BROADCASTER.stream_for_request(queue),
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
    
    # Extract diagnosis result text
    tool_text = [c.text for c in getattr(res, "content", [])][0] if getattr(res, "content", None) else "{}"
    try:
        parsed_diag = json.loads(tool_text)
    except Exception:
        parsed_diag = {}

    prop_id = parsed_diag.get("proposal", {}).get("id", "prop_replace_co_001") if isinstance(parsed_diag, dict) else "prop_replace_co_001"

    # Broadcast incident detection event
    event = {
        "type": "genius.event",
        "kind": "acoustic_incident",
        "title": "Acoustic Anomaly Detected",
        "message": "Hallway Carbon Monoxide detector chirping every 30s. Sensor end-of-life reached.",
        "severity": "critical",
        "entity_id": "ent_co_hallway",
        "proposal_id": prop_id,
        "actions": [
            {"id": "confirm", "label": "Order Replacement ($34.99)"},
            {"id": "dismiss", "label": "Dismiss"}
        ]
    }
    await SSE_BROADCASTER.broadcast(event)
    return JSONResponse({"status": "simulated", "tool_result": [c.text for c in getattr(res, "content", [])]})


@app.post("/simulate/delivery")
async def trigger_delivery_followup():
    """Simulates proactive delivery arrival: 'Your CO detector arrived today. Still chirping?'"""
    event = PROACTIVE_ENGINE.generate_delivery_followup(entity_id="ent_co_detector_hallway")
    await PROACTIVE_ENGINE.emit_proactive_event(event)
    return JSONResponse({"status": "event_broadcast", "event": event})


@app.post("/simulate/freeze")
async def trigger_freeze_warning(temp_f: float = 24.0):
    """Simulates freeze risk proactive warning."""
    event = PROACTIVE_ENGINE.generate_freeze_risk_warning(outdoor_temp_f=temp_f)
    if event:
        await PROACTIVE_ENGINE.emit_proactive_event(event)
        return JSONResponse({"status": "event_broadcast", "event": event})
    return JSONResponse({"status": "no_event", "reason": "Temperature above freezing threshold."})


@app.post("/simulate/real_chirp")
async def simulate_real_chirp():
    """Simulates diagnosing a verified physical smoke detector recording."""
    real_clip_path = "tests/clips/real_smoke_detector_chirp_819808.wav"
    await mcp_server.call_tool("hear_sound", {"clip_path": real_clip_path, "location": "hallway"})
    res_diag = await mcp_server.call_tool("diagnose", {
        "interval_s": 30.0,
        "peak_freq_hz": 3368.0,
        "duration_ms": 101.5,
        "location": "hallway",
        "clip_id": "real_smoke_detector_chirp_819808.wav"
    })
    
    event = {
        "id": f"evt_real_chirp_{uuid.uuid4().hex[:6]}",
        "type": "acoustic_detection",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "spoken_text": "That's your Kidde Smoke Detector in your hallway signaling a low battery with a 30-second chirp. I can guide you through replacing the battery when you're ready.",
        "card_title": "Verified Physical Chirp: Kidde Smoke Detector",
        "card_body": "Empirical recording match: 3,368 Hz piezo resonance, 101 ms pulse, 30s interval. Sourced from Bloofrzo (CC0). Raw audio was zero-wiped in RAM.",
        "actions": [
            {"id": "confirm", "label": "Order 9V Battery ($8.99)"},
            {"id": "dismiss", "label": "Dismiss"}
        ]
    }
    await SSE_BROADCASTER.broadcast(event)
    return JSONResponse({"status": "success", "diagnosis": [c.text for c in getattr(res_diag, "content", [])]})


# Mount Static Files for Client Simulator and Test Clips
app.mount("/clips", StaticFiles(directory="tests/clips"), name="clips")
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
