# Product Feedback & Friction Logs
**Amazon Developer Hackathon 2026**
*Submission Requirement: Feedback on every tool used + Friction Logs for up to 10% judging bonus.*

---

## 1. Product Feedback by Tool & SDK

### A. Model Context Protocol (MCP) Python SDK (v2.2.0)
- **What we used it for:** Building the self-hosted MCP server (`server/main.py`), registering 11 tools, and serving them over the Streamable HTTP transport spec (2025-11-25) mounted onto Starlette/FastAPI.
- **What worked well:** The `@server.tool()` decorator pattern is clean and intuitive; automatic Pydantic argument validation and schema generation worked seamlessly; ASGI integration via `streamable_http_app()` made mounting inside FastAPI straightforward.
- **What needs work:** Migration from MCP 1.x to 2.x had naming breaking changes (`FastMCP` renamed to `MCPServer`). Error messages returned over streamable HTTP can occasionally be swallowed into generic `UnexpectedToolError` without preserving inner tracebacks unless customized.
- **Onboarding experience:** 8/10. Documentation for stdio is abundant; documentation for Streamable HTTP transport in multi-protocol servers needs more real-world ASGI examples.
- **Would we build with it again?** Absolutely. MCP is rapidly becoming the universal protocol for agent tool-use.

### B. Amazon Bedrock (Anthropic Claude 3.5 Sonnet & Haiku)
- **What we used it for:** 
  1. Ingesting unstructured PDF/manual text and extracting structured acoustic signatures in `beepdb/ingest.py`.
  2. The Specialist Deliberation Panel in `tools/deliberate_repair.py` (evaluating equipment age, replacement cost, annual efficiency savings, and 5-year TCO economics).
  3. Multimodal vision parsing of appliance inspection tags and nameplates in `tools/register_entity.py`.
- **What worked well:** Claude 3.5 Sonnet's JSON mode adherence was flawless; zero schema hallucinations across 20 distinct device extractions. Inference latency on Bedrock was consistently sub-second for structured tasks.
- **What needs work:** Model access enablement in the AWS Console for brand-new AWS accounts still requires manual clicks across regions. Automated CDK/boto3 enablement would improve developer velocity.
- **Onboarding experience:** 9/10. The `boto3` `invoke_model` API with the Anthropic Messages format is rock solid.
- **Would we build with it again?** Yes, it is the premier choice for complex structured reasoning and specialist deliberation.

### C. Amazon Polly (Neural Voice Synthesis)
- **What we used it for:** Generating natural speech audio for proactive home maintenance alerts and 3 AM diagnostic readouts.
- **What worked well:** Neural voices (such as `Joanna` and `Matthew`) have vastly superior prosody and inflection compared to default browser speech synthesis; SSML support allows micro-tuning pauses for hardware cadence explanations.
- **What needs work:** SDK helper libraries could provide out-of-the-box streaming audio playback utilities for browser/client environments.
- **Onboarding experience:** 9.5/10. Simple, reliable, and instantaneous.
- **Would we build with it again?** Yes.

### D. Alexa+ Developer Preview & MCP Add-On Tooling
- **What we used it for:** Developing an Add-On Agent Skill architecture where Alexa+ acts as the living voice of the home world model.
- **What worked well:** The shift from classic rigid intent schemas to MCP tools is a massive leap forward. Developers can now expose pure functional logic rather than maintaining conversational slots and state machines.
- **What needs work:** The lack of unsolicited inbound server-to-device push sockets in the preview (which required us to build our own SSE Device Simulator to render proactive alerts).

---

## 2. Friction Logs (Judging Bonus Section)

### Friction Log #1: Unsolicited Inbound Push in Alexa+ MCP Add-ons
- **Task Attempted:** Pushing an unsolicited proactive alert to an Alexa+ device when a hardware incident occurs (e.g., replacement filter delivered, or sub-freezing weather risk).
- **Steps Taken:** Explored the Alexa+ MCP Toolkit documentation for server-initiated push notifications.
- **Expected vs. Actual:** Expected an MCP notification or webhook socket allowing the server to wake the Echo device. In reality, Alexa+ Preview currently only supports reactive request-response interactions initiated by the user's wake word.
- **Severity Rating:** Medium (Architectural Gap).
- **Workaround Used:** Implemented a Server-Sent Events (SSE) proactive transport (`proactive/transports/sse.py`) coupled with a branded, labeled Device Simulator client (`client/`) to showcase the experience, while maintaining a dormant spec push stub (`proactive/transports/mcp_push.py`).
- **Actionable Suggestion:** Provide an inbound webhook or persistent SSE client on Echo Show devices allowing verified MCP add-on servers to emit high-priority notifications with audio announcements.

### Friction Log #2: MCP 1.x to 2.x SDK Refactor
- **Task Attempted:** Initializing `FastMCP` per standard MCP tutorials.
- **Steps Taken:** Installed `mcp` via pip and imported `from mcp.server.fastmcp import FastMCP`.
- **Expected vs. Actual:** Expected `FastMCP` to initialize. The SDK threw `ModuleNotFoundError` stating that in MCP 2.x `FastMCP` was renamed to `MCPServer` in `mcp.server.mcpserver`.
- **Severity Rating:** Low (Documentation / Versioning).
- **Workaround Used:** Updated imports to `from mcp.server.mcpserver import MCPServer` and utilized `streamable_http_app()`.
- **Actionable Suggestion:** Maintain backward-compatible alias `FastMCP = MCPServer` with a `DeprecationWarning` rather than an immediate hard error in minor/major transitions.

### Friction Log #3: Zero-Crossing FFT Artifacts on Oscillating Piezo Pulses
- **Task Attempted:** Measuring exact pulse duration (milliseconds) of high-frequency piezo buzzers (3,200 Hz).
- **Steps Taken:** Thresholded raw PCM amplitudes against 25% peak energy.
- **Expected vs. Actual:** Expected contiguous ~80ms pulse duration. The raw sine wave crossed zero every 0.3ms, causing the energy detector to fragment the single pulse into dozens of sub-millisecond slices.
- **Severity Rating:** Medium (DSP Algorithm).
- **Workaround Used:** Implemented Hilbert transform amplitude envelope extraction (`signal.hilbert`) before thresholding in `audio/features.py`, ensuring smooth continuous pulse boundaries matching manufacturer specs.
- **Actionable Suggestion:** Include reference envelope DSP recipes in acoustic sensor SDK documentation for IoT audio classification.
