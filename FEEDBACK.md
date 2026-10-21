# Product Feedback & Friction Logs
**Amazon Developer Hackathon 2026**
*Submission Requirement: Feedback on every tool used + Friction Logs for up to 10% judging bonus.*

---

## 1. Product Feedback by Tool & SDK

### A. Model Context Protocol (MCP) Python SDK (`mcp` v2.2.0)
- **What we used it for:** Building the self-hosted MCP server (`server/main.py`), registering 12 tools, and serving them over the Streamable HTTP transport spec (`2025-11-25`) mounted onto Starlette/FastAPI.
- **What worked well:** The `@server.tool()` decorator pattern is clean and intuitive; automatic Pydantic argument validation and schema generation worked seamlessly; ASGI integration via `streamable_http_app()` made mounting inside FastAPI straightforward.
- **What needs work:**
  1. Migration from MCP 1.x to 2.x had breaking class renames (`FastMCP` renamed to `MCPServer` in `mcp.server.mcpserver`).
  2. When mounting `streamable_http_app()` inside a FastAPI application for a browser-based simulator, the SDK's internal `TransportSecurityMiddleware` rejects cross-origin `Origin` headers with `403 Invalid Origin header` even when FastAPI's `CORSMiddleware` is enabled, and `Mcp-Session-Id` must be explicitly added to `expose_headers`.
  3. `StreamableHTTPSessionManager.run()` raises a `RuntimeError` if entered more than once across test lifespans unless `_has_started` is reset.
- **Onboarding experience:** 8/10. Documentation for stdio is abundant; documentation for browser-accessible Streamable HTTP servers needs more ASGI/CORS examples.
- **Would we build with it again?** Absolutely. MCP is the universal protocol for agent tool-use.

### B. Amazon Bedrock (`amazon.nova-pro-v1:0`)
- **What we used it for:**
  1. The Specialist Deliberation Panel in `tools/deliberate_repair.py` (evaluating equipment age, replacement cost, annual efficiency savings, and 5-year TCO economics) using `amazon.nova-pro-v1:0`.
  2. Multimodal vision parsing of appliance inspection tags and nameplates in `tools/register_entity.py`.
- **What worked well:** Amazon Nova Pro (`amazon.nova-pro-v1:0`) is fast (~2.64s latency for multi-factor thermodynamic and financial analysis) and cost-effective.
- **What needs work:** Nova Pro frequently wraps structured JSON responses in markdown code fences (````json ... ````) or prepends conversational commentary despite system instructions requesting raw JSON only.
- **Onboarding experience:** 9/10. The `boto3` `invoke_model` API is reliable, and Nova Pro's price-to-performance ratio on Bedrock is strong.
- **Would we build with it again?** Yes.

### C. Amazon Polly (Neural Voice Synthesis)
- **What we used it for:** Generating natural speech audio (`Joanna` neural voice) for proactive home maintenance alerts and 3 AM diagnostic readouts.
- **What worked well:** Neural voices have natural prosody and low latency (~180 ms time-to-first-byte).
- **Onboarding experience:** 9.5/10. Simple, reliable, and fast.
- **Would we build with it again?** Yes.

### D. Alexa+ Simulated Experience Path (Building Without Gated Preview Console Access)
- **What we used it for:** Because the Alexa+ Developer Preview is gated behind partner allowlisting and identity verification, we followed the hackathon's permitted simulated-experience path—building a spec-compliant self-hosted MCP server (`POST /mcp`, spec `2025-11-25`) paired with a browser-based Alexa+ Preview Device Simulator (`client/app.js`).
- **What worked well:** The hackathon rules explicitly allow the simulated path and clearly specify what to showcase (context persistence across sessions, cards, and purchasing confirmation workflows).
- **What needs work:** Without access to the gated Alexa+ console, builders have no official offline Alexa+ MCP host emulator to verify how the Alexa+ runtime formats `tools/call` requests, renders visual card payloads, or handles proactive server-to-client events.

---

## 2. Friction Logs

### Friction Log #1: Gated Alexa+ Preview Access & Lack of an Offline Alexa+ MCP Host Emulator
- **Service / Track Tested:** Alexa+ Track (Simulated Experience Path / MCP `2025-11-25` Integration)
- **Task Attempted:** Testing how an Alexa+ host discovers and invokes our 12 MCP tools (`initialize` $\rightarrow$ `Mcp-Session-Id` $\rightarrow$ `tools/list` $\rightarrow$ `tools/call`) and renders companion visual cards without having gated Alexa+ partner console access.
- **Steps Taken:** Checked the Alexa+ developer portal and MCP specification (`2025-11-25`) to wire up a self-hosted Streamable HTTP MCP server and test conversational tool invocation.
- **Expected vs. Actual:**
  1. Expected a lightweight local CLI or browser-based "Alexa+ MCP Host Emulator" (similar to the classic Alexa Skills Kit simulator) that anyone can run locally without waiting for gated preview approval.
  2. Because no standalone Alexa+ MCP host emulator is publicly downloadable, we had to write our own browser-side MCP Streamable HTTP JSON-RPC 2.0 client (`client/app.js`) that negotiates `Mcp-Session-Id`, parses SSE-framed JSON-RPC responses (`event: message\ndata: {...}`), and renders card payloads, plus an out-of-band `/events` SSE channel to demonstrate proactive notifications.
- **Severity Rating:** Medium (Onboarding & Verification Friction for External Developers).
- **Workaround Used:** Built a full JSON-RPC 2.0 Streamable HTTP client in `client/app.js` talking directly to `POST /mcp`, added a voice-native conversational tool (`diagnose_from_description`) matching how Alexa+ extracts spoken parameters, and verified protocol compliance against the official Python `mcp` SDK in automated tests (`test_mcp_streamable_http_spec_handshake`).
- **Actionable Suggestion:** Publish an open-source `@amazon/alexa-plus-mcp-emulator` npm/pip package so developers outside the gated preview can validate MCP Streamable HTTP handshakes, card schemas, and proactive notification hooks locally.

---

### Friction Log #2: MCP Python SDK (`mcp` v2.2.0) `TransportSecurityMiddleware` Blocking Browser CORS Clients (`403 Invalid Origin`)
- **Service / Library Tested:** Model Context Protocol Python SDK (`mcp==2.2.0`, `MCPServer.streamable_http_app`)
- **Task Attempted:** Connecting our browser-based Alexa+ Device Simulator (`client/app.js`) directly to `POST /mcp` using JSON-RPC 2.0 (`initialize` and `tools/call`) across origins.
- **Steps Taken:** Mounted `mcp_server.streamable_http_app(streamable_http_path="/mcp")` inside FastAPI and configured `CORSMiddleware(allow_origins=["*"])`.
- **Expected vs. Actual:**
  1. Expected browser `fetch("${API_BASE}/mcp", { method: "POST" })` requests to succeed once FastAPI `CORSMiddleware` was configured.
  2. Instead, `mcp.server.transport_security.TransportSecurityMiddleware` intercepted the request inside the mounted sub-app and returned `403 Forbidden (Invalid Origin header)` whenever a browser sent an `Origin` header from a hosted simulator domain. Additionally, browsers hid the `mcp-session-id` response header from JavaScript until `expose_headers=["Mcp-Session-Id", "mcp-session-id"]` was explicitly added to `CORSMiddleware`.
- **Severity Rating:** Medium (Breaks Browser-Based MCP Clients Out of the Box).
- **Workaround Used:** Added `expose_headers=["Mcp-Session-Id", "mcp-session-id"]` to FastAPI's `CORSMiddleware` and normalized the internal ASGI scope headers in `server/main.py` before handing off to `mcp_app`, verified by `test_simulator_mcp_client_and_cors_session_header`.
- **Actionable Suggestion:** Expose an `allowed_origins: list[str]` parameter directly on `MCPServer.streamable_http_app()` and automatically include `Access-Control-Expose-Headers: Mcp-Session-Id` when CORS is enabled.

---

### Friction Log #3: Markdown Code-Fencing in Amazon Bedrock Nova Pro (`amazon.nova-pro-v1:0`) Structured JSON Outputs
- **Service Tested:** Amazon Bedrock Runtime (`amazon.nova-pro-v1:0` via `boto3` `invoke_model`)
- **Task Attempted:** Generating strictly valid JSON output for the 5-year TCO repair-vs-replace deliberation tool (`tools/deliberate_repair.py`).
- **Steps Taken:** Prompted `amazon.nova-pro-v1:0` with explicit instructions: `"Return ONLY valid JSON matching this schema: {...}. Do NOT include markdown code fences or conversational text."`
- **Expected vs. Actual:** Expected raw JSON directly parseable via `json.loads()`. Nova Pro frequently wrapped the JSON object in ````json ... ```` code blocks or prepended conversational text, causing `json.JSONDecodeError`.
- **Severity Rating:** Medium (Reliability Risk in Agent Tooling).
- **Workaround Used:** Implemented `parse_json_from_llm()` in `tools/utils.py` (tested in `test_parse_json_from_llm`) to strip Markdown fences and extract the outermost balanced JSON object before parsing.
- **Actionable Suggestion:** Support a native `response_format={"type": "json_schema", "schema": {...}}` parameter in the Bedrock `InvokeModel` / `Converse` API for Amazon Nova models to guarantee schema-valid JSON without regex post-processing.
