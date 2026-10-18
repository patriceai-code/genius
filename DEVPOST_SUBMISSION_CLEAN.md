# GENIUS — Devpost Submission (Clean Copy-Paste Format)

> **Instructions for Submitting on Devpost:**
> 1. Log into your project on [Devpost](https://amazonappdev2026.devpost.com/).
> 2. Paste Section 1 into project metadata / links.
> 3. Paste Section 2 into the **"About the Project"** description field (all formulas have been converted from LaTeX to crisp Unicode so Devpost renders them cleanly without broken math markup).
> 4. Paste Section 3 into the **"Friction Logs / Feedback"** fields.

---

## 1. Project Metadata & Links

- **Project Title:** GENIUS — Graph Engine for Networked Infrastructure Understanding & Service
- **Tagline:** Every place has a genius. Yours finally speaks.
- **Primary Track:** Alexa+
- **Mini-Challenges Entered:**
  - AWS Builder (Amazon Bedrock Nova Pro Deliberation, Tag Vision & Polly Neural TTS)
  - Open Source (Public MIT repository + Standalone `beepdb` acoustic database package)
- **Primary Repository:** https://github.com/patriceai-code/genius
- **Open Source Library (`beepdb`):** https://github.com/patriceai-code/beepdb
- **Live AWS Cloud Simulator:** http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com
- **Licenses:** MIT License (code) / Creative Commons Attribution 4.0 International (CC-BY 4.0 data)

---

## 2. "About the Project" (Copy & Paste directly into Devpost)

### The Problem & Economic Stakes: The 3:14 AM Crisis

Across 142 million US housing units (US Census Bureau), homes contain dozens of unmonitored piezoceramic transducers and buzzers: smoke alarms, carbon monoxide detectors, dehumidifiers, water leak sensors, and refrigerator evaporators. When these devices malfunction or expire, they emit an ambiguous, piercing chirp.

For ten thousand years of humans living in houses, no home has ever been able to say what is wrong. The consequence is not merely groggy frustration at 3:14 AM; it is catastrophic economic and physical loss:

* **$12,514 Average Water Damage Loss:** Undetected appliance overflows and leak sensor beeps that go unaddressed cause over $12,514 in residential water damage and mold remediation *(Source: Insurance Information Institute / ISO Homeowners Claim Study)*.
* **$15,000–$20,000 Frozen Pipe Bursts:** Aging furnaces locking out during sub-freezing cold snaps freeze residential plumbing within 28 hours *(Source: State Farm Winter Storm Claims Data)*.
* **$89–$150 Unnecessary Truck Rolls:** Homeowners routinely pay $89–$150 service dispatch fees for technicians simply to replace a 9V battery or reset a tripped breaker *(Source: HomeAdvisor / Angi 2024 Trade Survey)*.
* **Life Safety Failures:** Residential alarm studies *(CPSC & NFPA)* indicate homeowners frequently mistake the 30-second end-of-life expiration chirp for a low-battery alert, swap the battery, and leave an expired chemical sensor monitoring lethal gas.

**GENIUS** (*Graph Engine for Networked Infrastructure Understanding & Service*) is a self-hosted Model Context Protocol (MCP) server (spec 2025-11-25, Streamable HTTP transport) that gives the home a persistent mental model. Rather than treating Alexa as a voice frontend calling isolated tools from a drawer, GENIUS treats the home as an evolving physical world model that Alexa **wears**.

---

### Architecture & The 3-Pillar Engine (Zero Black-Box)

GENIUS does not rely on vague prompt engineering or black-box LLM guessing. It executes through a bounded, verifiable three-pillar architecture:

```
[Acoustic Audio / Piezo Chirp]
       │
       ▼ (Pillar 1: Deterministic Ephemeral DSP <15ms)
[Hilbert Analytic Envelope A(t) + Hann-Window FFT Peak Detection]
       │
       ▼ (Volatile Zero-Wipe RAM Scrubbing: 0 Bytes Stored to Disk)
[beepdb Signature Match: 20 Calibrated Device Fingerprints]
       │
       ▼ (Pillar 2: Persistent Mathematical World-Model)
[Home Graph: Weibull Hazard Reliability R(t) + Building Thermodynamics dT/dt]
       │
       ▼ (Pillar 3: Amazon Bedrock & Alexa+ Proactivity)
[Nova Pro 5-Yr TCO Deliberation in 2.6s · Propose -> Confirm · SSE Push to Tablet]
```

#### Pillar 1: Deterministic Ephemeral DSP (<15ms Local Processing)
High-frequency (3 kHz+) oscillating piezo square waves break classic zero-crossing algorithms. GENIUS computes the continuous analytic signal envelope using the Hilbert transform:
```
Envelope: A(t) = |s(t) + i · H{s(t)}|
```
This extracts the exact physical feature triplet: `(cadence interval, peak frequency, pulse duration)`. Audio is ingested ephemerally in volatile RAM and immediately cleared best-effort via `data.fill(0.0)`. Audio is never written to disk, logs, or persistent SQLite DB (verified by automated scan test `test_audio_never_persisted_to_disk_or_db`).

#### Pillar 2: Persistent Mathematical World-Model (Continuous Reliability & Thermodynamics)
The home does not jump between arbitrary state labels. Equipment health is continuously governed by two-parameter Weibull reliability distributions:
```
Reliability: R(t) = exp(-(t / η)^β)
Hazard Rate: h(t) = (β / η) · (t / η)^(β - 1)
```
*(e.g. CO Detector: η = 7.0 years, β = 3.0 wear-out exhaustion; HVAC Furnace: η = 15.0 years, β = 2.2 thermal fatigue).*

Before issuing proactive warnings, the Proactive Engine numerically simulates residential heat loss using a lumped-capacitance differential equation:
```
dT_in / dt = -(1 / τ) · (T_in - T_out) + (Q_furnace / C_thermal)
```
Evaluating counterfactual futures: For vulnerable pipe zones in unheated cavities (τ_pipe ≈ 16.0 hours), an unmitigated furnace trip at 24°F outdoor ambient causes pipe temperatures to hit freezing (32°F) in:
```
t = -16.0 · ln(8 / 44) = 27.3 hours
```
Conditioned on this prior (τ_pipe ~ Lognormal(ln(16), 0.3)), a 5,000-run Monte Carlo simulation establishes a **94.1% empirical freeze risk** within 48 hours (with 10th percentile freeze occurring in as little as **~18.2 hours**).

#### Pillar 3: Amazon Bedrock Specialist Deliberation & Alexa+ Proactivity
* **Amazon Bedrock Nova Pro (`amazon.nova-pro-v1:0`):** Evaluates multi-factor engineering economics—calculating 5-year repair vs. replace TCO, R-410A refrigerant phaseouts, and SEER energy efficiency payback periods in **2.6 seconds**.
* **Strict Propose → Confirm Trust Boundary:** The system stages structured replacement proposals; it **never** auto-executes financial transactions without explicit user authorization.
* **Server-Sent Events (SSE) Proactive Push:** Delivers unprompted ambient notices to the labeled Device Simulator when a replacement arrives (*"Your Kidde replacement arrived today. Still chirping?"*) or ahead of deep freeze risks.

---

### Empirical Validation, Statistics & Proof of Code

To eliminate blind trust, GENIUS includes an automated empirical benchmark suite and 19 automated tests verifying spec compliance and physical performance:

| Benchmark Dimension | Measured Result | Verification Receipt & Method |
| :--- | :--- | :--- |
| **Synthetic Baseline Corpus** | **95.0% (19/20)** | Evaluated across 20 appliance classes (smoke, CO, leaks, fridges, UPS) |
| **Empirical Physical Piezos** | **100.0% (6/6)** | Verified on real hardware recordings (Bloofrzo CC0 piezo transducers) |
| **Ambient Noise Robustness** | **90.0% (9/10)** | Mixed with real domestic room noise bed at **+15 dB SNR** |
| **Heavy Noise Gate** | **90.0% (9/10)** | Mixed under loud kitchen/domestic noise at **+6 dB SNR** |
| **DSP Feature Extraction** | **9.80 ms** | In-flight Hann-windowed FFT + Hilbert amplitude envelope |
| **Volatile In-Flight Scrubbing** | **0.005 ms** | In-memory zeroing via `data.fill(0.0)`; 0 raw audio bytes persisted |
| **beepdb Signature Search** | **0.015 ms** | 20-device signature search against physical tolerance bands |
| **Home Graph Ledger Write** | **3.70 ms** | SQLite persistent write with full auditable provenance |
| **Total Local Pipeline Latency**| **13.52 ms** | Real-time edge latency (exact sum of local components) |
| **Bedrock Deliberation Latency**| **2,640 ms** | Live Amazon Nova Pro structured JSON TCO deliberation |
| **Polly Neural TTS TTFB** | **180 ms** | Live Amazon Polly neural streaming (`Joanna`) |
| **Automated Test Suite** | **19/19 Passing (6.64s)** | Python 3.11 & 3.12 matrix on GitHub Actions CI |

---

### Viable Business Model & Market Viability

GENIUS transforms Alexa from a passive voice utility into an essential home infrastructure custodian with four high-margin revenue streams:

1. **High-Intent Prime Consumables & Hardware Fulfillment (45%):**
   When an end-of-life chirp or low battery occurs, GENIUS stages a 1-click verified replacement order directly to Amazon Prime (e.g. Kidde KN-COPP-3 $34.99 replacement unit or Energizer 9V 4-pack $8.99). Amazon captures immediate retail GMV on high-urgency, non-price-sensitive purchases.
2. **Insurance Carrier Telemetry & Loss-Mitigation Partnerships (30%):**
   Water leak and pipe freeze claims account for over $15 billion annually in US property insurance payouts. By mitigating catastrophic freeze bursts and slow leaks through predictive thermodynamics, Amazon can partner with carriers (State Farm, Nationwide, Aviva) to subsidize Alexa+ subscriptions for policyholders.
3. **The Killer Differentiator for Alexa+ Subscriptions (15%):**
   Subscribers do not pay $9.99/month for conversational timers; they pay for proactive protection that prevents $12,500 flood disasters and explains 3 AM panic beeps with epistemic certainty.
4. **Automated Manufacturer Warranty Claim Recovery (10%):**
   GENIUS automatically files structured warranty claim dossiers for failed in-warranty equipment, recovering $300–$1,500 in replacement costs for homeowners while establishing an auditable appliance provenance registry.

---

### Alignment with Official Hackathon Judging Criteria

| Judging Criterion | How GENIUS Fulfills Evaluation Criteria | Empirical Proof / Receipt |
| :--- | :--- | :--- |
| **1. Tech Implementation**<br>*(Execution & Tech Leverage)* | • **Alexa+ Track:** 100% compliant self-hosted FastMCP Server speaking **MCP Streamable HTTP (2025-11-25)**, validated with the official MCP Python SDK `StreamableHTTPClient` reference client.<br>• **12 Strictly Typed Tools:** Includes voice-native `diagnose_from_description` as well as companion mic `hear_sound`.<br>• **AWS Builder Mini-Challenge:** 100% Amazon infrastructure using **Amazon Bedrock Nova Pro** (`amazon.nova-pro-v1:0`) for 5-yr TCO deliberation & tag vision, **Amazon Polly Neural TTS** (`Joanna`), and **AWS S3 Static Website Hosting**.<br>• **Open Source Mini-Challenge:** Standalone package [`beepdb`](https://github.com/patriceai-code/beepdb) with CLI, MIT code, and CC-BY 4.0 data.<br>• **Sub-15ms DSP & Zero Storage:** Hilbert transform analytic envelope A(t) and volatile memory scrubbing proving zero bytes stored to disk. | • **19/19 Passing Tests** on Python 3.11/3.12 CI.<br>• **Total Local Pipeline Latency:** **13.52 ms**.<br>• **100% Physical Accuracy** on Bloofrzo CC0 piezo hardware.<br>• Live Bedrock Nova Pro latency: **2,640 ms**.<br>• Polly Neural TTS TTFB: **180 ms**. |
| **2. Design**<br>*(Coherence & Platform Fit)* | • **Voice-First Multimodal Synergy:** Designed specifically for Echo & Alexa+ preview devices. Natural voice handles the immediate acoustic query, while the visual surface (tablet simulator / Echo Show) renders rich **Acoustic Evidence Cards** with manual citations without verbal clutter.<br>• **The House Speaks First:** Proactive Server-Sent Events (SSE) push unprompted amber notification cards when a replacement part arrives.<br>• **Strict Propose → Confirm Trust Boundary:** Protects customer peace-of-mind by never executing transactions without explicit confirmation.<br>• **Privacy Surface:** *"What Does GENIUS Know?"* provides transparent provenance inspection and consent toggles. | • **Live Cloud Simulator:** Hosted on AWS S3 with interactive demo controls and 28 CC0 audio test clips.<br>• **ADR 001, 002, 003** documenting clean architectural patterns. |
| **3. Potential Impact**<br>*(Customer Need & Viability)* | • **Ubiquitous Need:** Solves the 3:14 AM chirping crisis across residential homes containing unmonitored piezoceramic transducers.<br>• **Massive Loss Prevention:** Prevents **$12,500** average water flood claims and **$15,000+** frozen pipe bursts via continuous building thermodynamics.<br>• **Life Safety:** Eliminates the fatal confusion where homeowners mistake expired CO alarms for low batteries.<br>• **Viable Beyond Hackathon:** 4 sustainable revenue engines: Prime fulfillment GMV (45%), carrier loss-mitigation telemetry (30%), Alexa+ $9.99/mo retention (15%), and warranty claim recovery (10%). | • **Lumped-Capacitance Math:** Predicts pipe zone freezing in 27.3 hours at 24°F (τ_pipe = 16.0h); 5,000-run Monte Carlo yields **94.1% freeze risk**.<br>• Fully articulated business model with unit economics. |
| **4. Quality of the Idea**<br>*(Creativity & Ecosystem Mastery)* | • **From Chatbot to World-Model:** Transcends naive LLM wrappers by giving the home a continuous physical mental model that Alexa **wears**.<br>• **Mathematical Rigor:** Continuous two-parameter Weibull reliability distributions (R(t) = exp(-(t/η)^β)) and dynamic fleet scores.<br>• **Acoustic Privacy by Construction:** Overcomes smart home audio surveillance anxiety by actively clearing buffers immediately after FFT feature extraction and verifying zero disk retention.<br>• **Deep MCP Ecosystem Mastery:** Pioneers spec-compliant proactive push patterns over Streamable HTTP and structured proposal workflows. | • [github.com/patriceai-code/genius](https://github.com/patriceai-code/genius)<br>• [github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb)<br>• 12 registered MCP tools conforming to spec 2025-11-25. |

---

## 3. Product Feedback & Friction Logs (Copy & Paste into Devpost Feedback fields)

### Friction Log #1: Alexa+ Preview MCP Push Socket Asymmetry
- **Component / Service:** Alexa+ Preview / Model Context Protocol (MCP) Streamable HTTP Transport (spec 2025-11-25)
- **Severity:** Medium (Architectural Gap in Proactive Experiences)
- **Problem Statement:** The Alexa+ Developer Preview MCP specification defines client-initiated Streamable HTTP sessions (`POST /mcp` with SSE responses), but does not define a standard bidirectional push channel for unprompted, agentic proactivity (e.g. ambient device alerts, delivery arrivals, freeze warnings).
- **Impact on Developer Velocity:** To demonstrate genuine proactivity, builders must maintain a parallel out-of-band SSE channel (`GET /events`) alongside `/mcp`. This creates state synchronization overhead between session-scoped MCP contexts and ambient device notifications.
- **Suggested Improvement:** Add an official `notifications/proactivePush` primitive or a bidirectional WebSocket/WebTransport binding to the MCP specification for Alexa+, allowing registered MCP servers to push ambient cards and proactive voice prompts directly into the Echo device's notification tray without requiring an explicit wake-word turn.

---

### Friction Log #2: Amazon Bedrock Structured Output Code-Fence Stripping
- **Component / Service:** Amazon Bedrock Runtime (`amazon.nova-pro-v1:0` / `InvokeModel` API)
- **Severity:** Medium (Developer Friction & Fragility in Agent Tooling)
- **Problem Statement:** When prompting Amazon Bedrock models to return strictly valid JSON matching an appliance deliberation schema, models frequently wrap the JSON response in Markdown code fences (e.g. ````json { ... } ````) or include conversational preambles/postambles despite system prompts requesting raw JSON only.
- **Impact on Developer Velocity:** Downstream MCP tool handlers fail on `json.loads()` unless developers write defensive regex pre-processors to strip code fences and extract the outermost balanced JSON object.
- **Suggested Improvement:** Introduce a first-class `response_format={"type": "json_schema", "schema": {...}}` parameter on `InvokeModel` across all Bedrock foundation models (similar to JSON Schema enforcement in OpenAI and Anthropic direct APIs), guaranteeing parseable structured outputs without client-side regex workarounds.

---

### Friction Log #3: AWS S3 Website Hosting HTTPS & Root Domain Limitations
- **Component / Service:** AWS S3 Static Website Hosting
- **Severity:** Low (Operational Overhead for Rapid Hackathon Prototypes)
- **Problem Statement:** S3 static website hosting endpoints only serve plain HTTP (`http://bucket-name.s3-website.region.amazonaws.com`). Enabling HTTPS requires provisioning an Amazon CloudFront distribution, requesting an AWS Certificate Manager (ACM) SSL certificate in `us-east-1`, and configuring DNS CNAMEs.
- **Impact on Developer Velocity:** For fast-paced hackathons, builders deploying web-based device simulators to S3 encounter mixed-content security warnings when web clients attempt to connect to secure backends, adding ~30 minutes of CloudFront propagation wait time.
- **Suggested Improvement:** Provide native TLS/HTTPS on the default S3 website endpoints (e.g. `https://bucket-name.s3-website.region.amazonaws.com`) using default wildcard certificates, eliminating the mandatory CloudFront distribution requirement for simple developer prototypes.
