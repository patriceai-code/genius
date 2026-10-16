# Product Feedback & Friction Logs
**Amazon Developer Hackathon 2026**
*Submission Requirement: Feedback on every tool used + Friction Logs for up to 10% judging bonus.*

---

## 1. Product Feedback by Tool & SDK

### A. Model Context Protocol (MCP) Python SDK (v2.2.0)
- **What we used it for:** Building the self-hosted MCP server (`server/main.py`), registering 12 tools, and serving them over the Streamable HTTP transport spec (2025-11-25) mounted onto Starlette/FastAPI.
- **What worked well:** The `@server.tool()` decorator pattern is clean and intuitive; automatic Pydantic argument validation and schema generation worked seamlessly; ASGI integration via `streamable_http_app()` made mounting inside FastAPI straightforward.
- **What needs work:** Migration from MCP 1.x to 2.x had naming breaking changes (`FastMCP` renamed to `MCPServer`). Error messages returned over streamable HTTP can occasionally be swallowed into generic `UnexpectedToolError` without preserving inner tracebacks unless customized.
- **Onboarding experience:** 8/10. Documentation for stdio is abundant; documentation for Streamable HTTP transport in multi-protocol servers needs more real-world ASGI examples.
- **Would we build with it again?** Absolutely. MCP is rapidly becoming the universal protocol for agent tool-use.

### B. Amazon Bedrock (Amazon Nova Pro)
- **What we used it for:** 
  1. The Specialist Deliberation Panel in `tools/deliberate_repair.py` (evaluating equipment age, replacement cost, annual efficiency savings, and 5-year TCO economics) using `amazon.nova-pro-v1:0`.
  2. Multimodal vision parsing of appliance inspection tags and nameplates in `tools/register_entity.py`.
- **What worked well:** Amazon Nova Pro (`amazon.nova-pro-v1:0`) is exceptionally fast—deliberation latency was ~2.64s for complex multi-factor thermodynamic and financial calculations; multimodal vision accurately identified equipment model tags from photos.
- **What needs work:** Nova Pro occasionally wraps structured JSON responses in markdown code fences (````json ... ````) or prepends conversational commentary ("Here is the financial analysis:"), which breaks standard `json.loads` deserialization unless cleaned with regex extractors.
- **Onboarding experience:** 9/10. The `boto3` `invoke_model` API is reliable, and Nova Pro's price-to-performance ratio on Bedrock is outstanding.
- **Would we build with it again?** Yes, Nova Pro is our default production deliberation engine.

### C. Amazon Polly (Neural Voice Synthesis)
- **What we used it for:** Generating natural speech audio for proactive home maintenance alerts and 3 AM diagnostic readouts.
- **What worked well:** Neural voices (such as `Joanna` and `Ruth`) have vastly superior prosody and inflection compared to default browser speech synthesis; SSML support allows micro-tuning pauses for hardware cadence explanations. Time-to-first-byte (TTFB) streaming was measured at ~180 ms.
- **What needs work:** The AWS Python SDK (`boto3`) returns an `AudioStream` object, but helper libraries could provide out-of-the-box browser Web Audio streaming utilities for frontend integration.
- **Onboarding experience:** 9.5/10. Simple, reliable, and instantaneous.
- **Would we build with it again?** Yes.

### D. Alexa+ Developer Preview & MCP Add-On Tooling
- **What we used it for:** Developing an Add-On Agent Skill architecture where Alexa+ acts as the living voice of the home world model.
- **What worked well:** The shift from classic rigid intent schemas to MCP tools is a massive leap forward. Developers can now expose pure functional logic rather than maintaining conversational slots and state machines.
- **What needs work:** The lack of unsolicited inbound server-to-device push sockets in the preview (which required us to build our own SSE Device Simulator to render proactive alerts), and the architectural distinction between voice conversation arguments vs. companion mic streaming.

---

## 2. Friction Logs (Judging Bonus Section)

### Friction Log #1: Unsolicited Inbound Push & Voice-First Input in Alexa+ MCP Add-ons
- **Service Tested:** Alexa+ Developer Preview & MCP Add-On Toolkit
- **Task Attempted:** Pushing an unsolicited proactive maintenance alert to an Alexa+ device when a hardware incident occurs (e.g., replacement delivery or sub-freezing weather risk), and diagnosing sounds from room audio.
- **Steps Taken:** Explored the Alexa+ MCP Toolkit documentation for server-initiated push notifications and raw audio ingestion.
- **Expected vs. Actual:** 
  1. Expected an MCP notification webhook socket allowing the server to wake the Echo device unprompted. In reality, Alexa+ Preview currently only supports reactive request-response interactions initiated by the user's wake word.
  2. Expected an audio stream tool parameter. In reality, Alexa+ passes structured arguments extracted from user speech by the model, rather than raw room audio.
- **Severity Rating:** Medium (Architectural Gap).
- **Workaround Used:** 
  1. Implemented a Server-Sent Events (SSE) proactive transport (`proactive/transports/sse.py`) coupled with a branded, labeled Device Simulator client (`client/`) to showcase the experience, while maintaining a dormant spec push stub (`proactive/transports/mcp_push.py`).
  2. Implemented a voice-native diagnostic tool (`diagnose_from_description`) where Alexa prompts the user for verbal cues (*"How many seconds between chirps? Single or double chirp?"*), while reserving raw audio processing (`hear_sound`) for companion edge microphones (e.g. mobile app or ESP32 mic).
- **Actionable Suggestion:** 
  1. Provide an inbound webhook or persistent SSE client on Echo Show devices allowing verified MCP add-on servers to emit high-priority notifications with audio announcements.
  2. Add an optional "acoustic listening" permission grant allowing certified MCP tools to request a 5-second raw audio buffer from Echo far-field microphones when a user says "Alexa, what's that sound?".

### Friction Log #2: Markdown Code-Fencing in Amazon Bedrock Nova Pro Structured JSON
- **Service Tested:** Amazon Bedrock (Amazon Nova Pro `amazon.nova-pro-v1:0`)
- **Task Attempted:** Generating structured JSON output for the Engineering Deliberation panel (`tools/deliberate_repair.py`) evaluating 5-year TCO repair-vs-replace decisions.
- **Steps Taken:** Formatted prompt system instruction with: `"Return ONLY valid JSON matching this schema: {...}. Do NOT include markdown code fences or conversational text."`
- **Expected vs. Actual:** Expected a pure JSON string directly deserializable via `json.loads()`. Nova Pro frequently wrapped valid JSON in ````json\n{...}\n```` code blocks or prepended conversational introductory phrases ("Here is the economic deliberation analysis:"), resulting in `json.decoder.JSONDecodeError`.
- **Severity Rating:** Medium (Developer Friction / Reliability Risk).
- **Workaround Used:** Authored a resilient JSON parser `parse_json_from_llm` in `tools/utils.py` that utilizes regex outer-brace matching (`r'\{[\s\S]*\}'`) to isolate and extract the valid JSON payload before deserialization.
- **Actionable Suggestion:** Implement a native `response_format={"type": "json_object"}` parameter or grammar-constrained sampling in the Bedrock Runtime `InvokeModel` API for Amazon Nova models, guaranteeing that tokens outside valid JSON grammar cannot be generated.

### Friction Log #3: AWS S3 Static Website Hosting Lack of Native TLS/HTTPS for Web Audio APIs
- **Service Tested:** Amazon S3 (Static Website Hosting)
- **Task Attempted:** Deploying the interactive Alexa+ Preview Device Simulator web app to AWS for public hackathon demonstration and testing.
- **Steps Taken:** Enabled Static Website Hosting on S3 bucket `genius-simulator-115207986956` and applied public read bucket policies via `boto3`.
- **Expected vs. Actual:** The S3 static website endpoint (`http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com`) serves strictly over unencrypted HTTP. Modern browser security models (W3C Secure Contexts specification) disable `navigator.mediaDevices.getUserMedia` and Web Audio microphone capture on non-HTTPS origins, preventing live microphone capture in the web browser.
- **Severity Rating:** Medium (Deployment Complexity).
- **Workaround Used:** Pre-packaged 28 CC0 and CC-BY audio benchmark clips directly into the S3 bucket under `/clips/`, allowing users and judges to simulate both synthetic and empirical physical piezo chirps with 1-click playback over HTTP without needing microphone permission.
- **Actionable Suggestion:** Add a 1-click "Enable CloudFront HTTPS Distribution" checkbox in the Amazon S3 Static Website Hosting console configuration (or an automated `boto3` helper), automatically provisioning a free AWS Certificate Manager (ACM) TLS certificate and CloudFront distribution.
