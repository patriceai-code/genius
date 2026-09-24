# Amazon Developer Hackathon 2026 — Devpost Submission Package

Use this document to copy and paste your submission directly into the [Devpost Submission Form](https://amazonappdev2026.devpost.com/).

---

## 1. Submission Metadata

- **Project Title:** GENIUS — Graph Engine for Networked Infrastructure Understanding & Service
- **Tagline:** *Every place has a genius. Yours finally speaks.*
- **Primary Track:** Alexa+
- **Mini-Challenges Entered:**
  1. **AWS Builder** (Amazon Bedrock Claude 3.5 Sonnet Specialist Deliberation, Multimodal Tag Vision & Polly TTS)
  2. **Open Source** (Public MIT repo + Standalone `beepdb` acoustic database package)
- **Primary Repository URL:** https://github.com/patriceai-code/genius
- **Open Source Mini-Challenge Package URL (`beepdb`):** https://github.com/patriceai-code/beepdb
- **Open Source License:** MIT License (Main repository and BeepDB package) / CC-BY 4.0 (Acoustic citations)


---

## 2. Devpost Text Description (Copy & Paste)

### The Elevator Pitch
*It's 3:14 AM and something in your home is chirping.* Smoke detector? Carbon monoxide? Fridge door? Low battery? In ten thousand years of humans living in houses, no house has ever been able to say it.

**GENIUS** is a self-hosted Model Context Protocol (MCP) server (spec 2025-11-25, Streamable HTTP transport) that gives a home a persistent mind: a living graph of every device, incident, warranty, and physical material. Not a drawer of tools Alexa calls: a world model Alexa wears.

### Key Capabilities
1. **The House Hears:** *"Alexa, what's that sound?"* The chirp is matched against `beepdb`, a growing library of 20 verified device signatures mapped from official manufacturer documentation.
   - *"That's your CO detector's end-of-life chirp — not a low battery. Hallway unit, manufactured 2018. Replacement on the way."*
2. **The House Proposes, Never Acts:** Strict **Propose $\rightarrow$ Confirm** architecture. The system never executes purchases or external mutations autonomously. Acoustic processing is **ephemeral by design** — FFT spectral peaks and cadence features are extracted in-flight, and raw audio buffers are immediately zero-wiped in RAM before returning.
3. **The House Speaks First:** Server-Sent Events (SSE) push transport delivers unprompted proactive intelligence to a labeled Device Simulator client when a replacement arrives (*"Your Kidde replacement arrived today. Still chirping?"*) or when sub-freezing weather threatens an aging furnace.
4. **Day 0 Onboarding & Warranties:** Snap a photo of an equipment label; Bedrock Claude 3.5 extracts model numbers and registers 10-year manufacturer warranty coverage into the Home Graph.
5. **Specialist Deliberation Panel (AWS Builder):** When a furnace or water heater fails, Alexa+ consults an Amazon Bedrock Engineering Specialist to calculate repair cost vs replacement payback, annual energy savings, and five-year TCO.

### How We Built It
- **MCP Server:** Python MCP SDK 2.x (`mcp.server.mcpserver`) with Streamable HTTP transport mounted onto FastAPI / Starlette.
- **Persistent World Model:** SQLite Home Graph with strict data provenance auditing on every entity and incident write.
- **Acoustic Intelligence:** SciPy and NumPy Hilbert envelope extraction, Fast Fourier Transform (FFT) peak detection, and cadence interval estimation.
- **AWS Integration:**
  - **Amazon Bedrock (Anthropic Claude 3.5 Sonnet):** Automated extraction of beep codes from manuals, multimodal tag scanning, and the Specialist Deliberation Panel.
  - **Amazon Polly:** Neural voice synthesis for proactive audio notifications.
- **Simulator Client:** Single-page ES6 web client with native `EventSource` SSE listener, interactive action cards, and privacy provenance inspector.

### What We Learned & What's Next
Building with MCP 2.x and Streamable HTTP proved that exposing pure tool functions to frontier reasoning models enables richer agent behaviors than classic rigid conversational slots. Next on our roadmap: expanding `beepdb` to 100+ devices, automated warranty claim filing with insurance APIs, and multimodal acoustic diagnosis for unpatterned mechanical sounds (refrigerant leaks, motor bearing wear).

---

## 3. Product Feedback & Friction Logs (Copy & Paste)

*(Copy directly from [FEEDBACK.md](FEEDBACK.md) into the Devpost required feedback fields).*

---

## 4. Final Submission Checklist

- [ ] Ensure repo is public: [github.com/patriceai-code/genius](https://github.com/patriceai-code/genius) (or add reviewers if private).
- [ ] Record a video under 3:00 (following [demo/script.md](demo/script.md)).
- [ ] Upload video to YouTube (Public or Unlisted) and paste URL into Devpost.
- [ ] Paste the description from Section 2 into the Devpost "About the Project" box.
- [ ] Paste feedback from [FEEDBACK.md](FEEDBACK.md) into the Devpost Feedback fields.
- [ ] Select **Alexa+** as primary track, plus **AWS Builder** and **Open Source** mini-challenges.
- [ ] Submit before the deadline (Oct 23, 2026 @ 12:00 PM PDT)!
