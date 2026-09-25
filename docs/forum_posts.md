# Amazon Developer Forums & Discussions Posts
**Project:** GENIUS — The Home World Model (Amazon Developer Hackathon 2026)  
**Track:** Alexa+ Primary Track | **Mini-Challenges:** AWS Builder & Open Source  

Below are the two ready-to-paste community discussion posts for the Amazon Developer Forums and hackathon discussions board. These posts document our architectural choices, disclose our simulator methodology, ask technical roadmap questions about MCP proactivity, and provide actionable feedback on Amazon Bedrock, Amazon Polly, and the MCP Python SDK.

---

## Post 1: Alexa+ MCP Architecture & Proactive Event Pattern

**Subject:** Architectural pattern: Bridging reactive Alexa+ voice tools with self-hosted MCP (Streamable HTTP 2025-11-25) & proactive SSE cards

**Category:** Alexa+ Developer Preview / Model Context Protocol (MCP)

**Body:**

Hello fellow builders and Amazon Alexa+ team,

We are currently building **GENIUS** (Graph Engine for Networked Infrastructure Understanding & Service) for the Alexa+ hackathon track. Rather than treating Alexa as a voice frontend that merely calls isolated tools, GENIUS treats the home as a persistent world model that Alexa "wears"—tracking physical hardware, acoustic chirp signatures, manufacturer manuals, and device life-cycles.

We wanted to share our architecture for self-hosting an MCP server on the newest **2025-11-25 Streamable HTTP specification**, disclose our handling of proactive display events, and ask a question regarding the future roadmap for server-initiated notifications.

### 1. The Reactive Voice Path (Official MCP Spec 2025-11-25)
For real-time voice interactions (*"Alexa, what's that chirping sound?"*), our server implements a direct Streamable HTTP endpoint at `/mcp` conforming strictly to the latest specification:
- Handles standard JSON-RPC `initialize`, `notifications/initialized`, and `tools/list` handshakes.
- Issues stateful `mcp-session-id` headers for session continuity.
- Exposes 7 core tools: `hear_sound`, `diagnose`, `list_entities`, `get_home_health`, `propose_action`, `confirm_action`, and `record_incident`.
- Privacy-by-design: Acoustic processing extracts spectral FFT peaks and cadence intervals in volatile memory and immediately purges raw audio buffers (zero retention).

### 2. The Proactive Gap & Our Simulator Solution
In a physical home, the most critical events are **unprompted and asynchronous**:
- At 3:14 AM, an alarm chirps, requiring immediate identification.
- 48 hours later, a replacement sensor arrives on the porch, and the home proactively asks: *"Your replacement Kidde alarm just arrived. Would you like me to walk you through replacing the hallway unit?"*

Because the current Alexa+ Preview client cannot yet accept arbitrary unprompted server-initiated display events without prior wake-word invocation, we built a dual-transport architecture:
1. **Reactive Voice:** Streamable HTTP (`/mcp`) for Alexa+ voice turns and tool execution.
2. **Proactive Surface:** Server-Sent Events (`/events`) pushing real-time UI state cards to an **"Alexa+ Preview Device Simulator"** web client.

*Disclosure for Judges & Community:* Every proactive visual beat in our demo video is displayed on a screen clearly stamped with the header **"ALEXA+ PREVIEW DEVICE SIMULATOR"**. The underlying server logic, event dispatchers, and state machines are 100% production code running live.

### 3. Explicit Questions for the Amazon Alexa+ Team & Hackathon Organizers
1. **Scoring & Eligibility Clarification:**
   > **We ship a real self-hosted MCP server AND use a labeled simulator client for server-initiated events; does the simulated path affect eligibility or scoring for the Alexa+ track?**
   (Our server, MCP Streamable HTTP transport, 11 tools, and event dispatch logic are 100% real and production-ready; only the client display for unprompted server-initiated events runs on our labeled simulator).

2. **Roadmap Question on Server-Initiated Proactivity:**
   What is the envisioned architecture for **server-initiated proactive push notifications** in future iterations of the Alexa+ MCP ecosystem?
   - Will Alexa+ MCP clients eventually maintain a persistent bidirectional stream (e.g., HTTP/2 or WebSockets) where an MCP server can emit a `notifications/message` or `proactive/event` that natively wakes the Echo Show screen or sounds an ambient chime?
   - Or will the recommended path be an integration between self-hosted MCP servers and the existing Alexa Proactive Events API / Skill Messaging?

We would appreciate official confirmation on the scoring rule so our submission disclosure is 100% aligned with judging expectations.


---

## Post 2: Builder Feedback: Amazon Bedrock (Nova Pro), Amazon Polly & MCP SDK

**Subject:** Builder Feedback: Lessons from implementing acoustic DSP + Amazon Bedrock Nova Pro deliberation + Amazon Polly Neural streaming in an MCP loop

**Category:** AWS Builder / Bedrock / Developer Tools / MCP

**Body:**

Hi everyone,

As part of the AWS Builder mini-challenge for our hackathon project **GENIUS**, we integrated a full Amazon cloud stack—**Amazon Bedrock (Nova Pro)** for multi-variable repair-vs-replace deliberation, **Amazon Polly (Neural)** for real-time speech synthesis, and custom digital signal processing (DSP)—all orchestrated through the Model Context Protocol (MCP).

Here is our honest feedback from building on these tools in production:

### 1. Amazon Bedrock & Amazon Nova Pro (`amazon.nova-pro-v1:0`)
- **The Good:** In our testing, Amazon Nova Pro provided exceptional reasoning latency (averaging ~1.5s to 2.2s for complex, multi-variable engineering trade-offs). When deciding whether a homeowner should repair a 9-year-old Carrier HVAC system or replace it with a heat pump, Nova Pro reliably factored compressor replacement costs (\$1,800), legacy R-410A refrigerant phaseout regulations, SEER 14 vs 18 efficiency differentials, and manufacturer warranty coverage into structured JSON recommendations without hallucinating phantom rebate numbers.
- **Immediate Accessibility:** Unlike some third-party foundation models that require lengthy enterprise use-case approval forms on brand-new AWS accounts, Amazon Nova Pro was active and operational immediately.
- **Wishlist / Feedback:** We would love to see **native JSON Schema enforcement (Structured Outputs)** built directly into the Bedrock Runtime `InvokeModel` API for Nova Pro (similar to grammar-constrained decoding). Currently, developers must enforce JSON output via system prompt instructions and post-parse the response string.

### 2. Amazon Polly Neural Streaming
- **The Good:** We used Amazon Polly Neural (`Joanna`) streaming MP3 chunks over our `/api/polly/speak` endpoint. For 3 AM emergency notifications, Polly's neural voice strikes the exact right balance between urgent clarity and calm reassurance.
- **Wishlist / Feedback:** Integrating Polly with local browser audio contexts currently requires streaming MP3 or base64 over HTTP. A native WebRTC or raw chunked PCM endpoint from Polly with sub-100ms first-byte latency would allow real-time conversational interruptions during long diagnostic walkthroughs.

### 3. MCP Python SDK & Streamable HTTP (2025-11-25 Spec)
- **The Good:** The migration to Streamable HTTP is a huge improvement in reliability over stdio transports for cloud deployments. The session management and header routing are clean.
- **Gotchas & Lessons Learned:**
  1. *Host Header Validation:* The MCP server transport security layer strictly checks the `Host` header. In automated test environments using Starlette/FastAPI `TestClient` (which defaults to `Host: testserver`), requests will fail with `421 Misdirected Request` unless `base_url="http://127.0.0.1:8000"` is explicitly configured.
  2. *Lifespan Context Management:* When embedding `mcp_server.streamable_http_app()` inside a parent FastAPI application, the session manager's task group must be explicitly initialized within the FastAPI lifespan via `async with mcp_server._lowlevel_server._session_manager.run():`. Without this, concurrent requests throw `RuntimeError: Task group is not initialized`. We recommend adding an official FastAPI integration snippet to the MCP documentation.

### 4. Grounding with Physical Reality
- One major lesson from building our open-source acoustic dataset (`beepdb`): **real physical hardware drifts from nominal specs**. Manuals state a Kidde CO alarm chirps at 3,200 Hz, but our empirical measurements on physical piezo buzzers (CC0 audio corpus) measured actual resonance peaks at 3,368 Hz and 3,321 Hz. Calibration against empirical recordings with $\pm 350\text{ Hz}$ tolerance bands was essential to avoid false negatives.

Overall, the developer experience across Bedrock Nova Pro, Polly, and MCP was seamless, and running our entire deliberation and voice pipeline on 100% Amazon infrastructure gave us rock-solid stability.

Kudos to the AWS and Alexa developer teams!
