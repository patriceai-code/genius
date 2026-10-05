# Amazon Developer Hackathon 2026 — Devpost Submission Package

Use this document to copy and paste your submission directly into the [Devpost Submission Form](https://amazonappdev2026.devpost.com/).

---

## 1. Submission Metadata

- **Project Title:** GENIUS — Graph Engine for Networked Infrastructure Understanding & Service
- **Tagline:** *Every place has a genius. Yours finally speaks.*
- **Primary Track:** Alexa+
- **Mini-Challenges Entered:**
  1. **AWS Builder** (Amazon Bedrock Nova Pro Specialist Deliberation, Multimodal Tag Vision & Polly Neural TTS)
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
2. **The House Predicts (Continuous World-Model Physics):** Rather than arbitrary state flags, every hardware asset tracks continuous Weibull reliability distributions ($R(t) = \exp(-(t/\eta)^\beta)$). The proactive engine runs lumped-capacitance building thermodynamic simulations before staging alerts, calculating exact hours until unheated pipe freeze under sub-freezing weather.
3. **The House Proposes, Never Acts:** Strict **Propose $\rightarrow$ Confirm** architecture. The system never executes purchases or external mutations autonomously. Acoustic processing is **ephemeral by design** — FFT spectral peaks and cadence features are extracted in-flight, and raw audio buffers are immediately zero-wiped in RAM before returning.
4. **The House Speaks First:** Server-Sent Events (SSE) push transport delivers unprompted proactive intelligence to a labeled Device Simulator client when a replacement arrives (*"Your Kidde replacement arrived today. Still chirping?"*) or when sub-freezing weather threatens an aging furnace.
5. **Day 0 Onboarding & Warranties:** Snap a photo of an equipment label; Bedrock multimodal vision (Amazon Nova Pro / Claude Sonnet) extracts model numbers and registers manufacturer warranty coverage into the Home Graph.
6. **Specialist Deliberation Panel (AWS Builder):** When a furnace or water heater fails, Alexa+ consults an Amazon Bedrock Engineering Specialist (powered by Amazon Nova Pro `amazon.nova-pro-v1:0`) to calculate repair cost vs replacement payback, annual energy savings, and five-year TCO in 2.6 seconds.

### How We Built It
- **MCP Server:** Python MCP SDK 2.x (`mcp.server.mcpserver`) with Streamable HTTP transport mounted onto FastAPI / Starlette.
- **Persistent World Model:** SQLite Home Graph with continuous Weibull hazard decay scoring and strict data provenance auditing on every entity and incident write.
- **Acoustic Intelligence:** SciPy and NumPy Hilbert envelope extraction, Fast Fourier Transform (FFT) peak detection, and cadence interval estimation.
- **AWS Integration:**
  - **Amazon Bedrock (Amazon Nova Pro):** Multi-variable engineering deliberation (Repair vs Replace TCO) and multimodal nameplate photo tag OCR.
  - **Amazon Polly:** Neural voice synthesis (`Joanna` / `Ruth`) streaming natural voice alerts through the Device Simulator.
- **Simulator Client:** Single-page ES6 web client with native `EventSource` SSE listener, interactive action cards, and privacy provenance inspector.
- **Automated Verification:** 17/17 passing pytest suite verifying spec-compliant MCP 2025-11-25 handshake, ephemeral RAM scrub attestation, and two-level noise robustness (+15 dB and +6 dB SNR).

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
