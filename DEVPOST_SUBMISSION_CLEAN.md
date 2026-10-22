# GENIUS — Devpost Submission (Clean Copy-Paste Format)

> **Instructions for Submitting on Devpost:**
> 1. Log into your project on [Devpost](https://amazonappdev2026.devpost.com/).
> 2. Paste Section 1 into project metadata / links.
> 3. Paste Section 2 into the **"About the Project"** description field (all formulas use clean Unicode so Devpost renders them without broken math markup).
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
- **Live AWS Cloud Simulator (Offline Replay & Configurable MCP Host):** http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com
- **Licenses:** MIT License (code) / Creative Commons Attribution 4.0 International (CC-BY 4.0 data)

---

## 2. "About the Project" (Copy & Paste directly into Devpost)

### Executive Summary: What Is Real vs. Simulated

**GENIUS** (*Graph Engine for Networked Infrastructure Understanding & Service*) is a self-hosted **Model Context Protocol (MCP) server** (`spec 2025-11-25`, Streamable HTTP transport at `POST /mcp`) paired with a browser-based **Alexa+ Preview Device Simulator** (`client/app.js`).

* **What runs live in code:**
  1. **Spec-Compliant MCP Client-Server Handshake:** `client/app.js` connects directly to `POST /mcp` using JSON-RPC 2.0 (`initialize` → `Mcp-Session-Id` header → `notifications/initialized` → `tools/list` → `tools/call`) and renders UI cards dynamically from the MCP server's JSON responses.
  2. **12 MCP Tools:** Voice-native chirp diagnosis (`diagnose_from_description`), companion-sensor DSP feature extraction (`hear_sound` + `diagnose`), persistent SQLite Home Graph (`list_entities`, `get_home_health`, `register_entity`, `record_incident`), strict `propose_action` → `confirm_action` gate, warranty ledger (`check_warranty`, `file_warranty_claim`), and live **Amazon Bedrock Nova Pro** (`amazon.nova-pro-v1:0`) 5-year TCO deliberation (`deliberate_repair`).
  3. **Deterministic Signal Processing & Physics:** Hilbert transform amplitude envelope, Hann-windowed FFT, two-parameter Weibull hazard reliability (`R(t)`), and lumped-capacitance building heat-loss simulation (`dT/dt`) with 5,000-run Monte Carlo uncertainty quantification.
* **What is simulated (per Alexa+ Track guidelines):**
  - Because Alexa+ Preview is gated and does not stream raw room audio to third-party MCP servers, the primary Alexa+ path is conversational (`diagnose_from_description`), while `hear_sound` represents a companion sensor intake (e.g., mobile app or edge mic).
  - Package delivery (`POST /simulate/delivery`), weather drops (`POST /simulate/freeze`), and order fulfillment IDs (`AMZN-2026-94819-...`) are simulated state triggers to demonstrate multi-day lifecycles in a 2-minute demo.
  - When the static S3 simulator URL is opened without a local MCP server running, it explicitly displays an amber **`Offline Replay (No MCP Server Connected)`** badge.

---

### The Problem & Economic Stakes: The 3:14 AM Crisis

Across 142 million US housing units (US Census Bureau), homes contain dozens of unmonitored piezoceramic transducers and buzzers: smoke alarms, carbon monoxide detectors, dehumidifiers, water leak sensors, and refrigerator evaporators. When these devices malfunction or expire, they emit an ambiguous chirp:

* **$12,514 Average Water Damage Loss:** Undetected appliance overflows and leak sensor beeps that go unaddressed cause over $12,514 in residential water damage *(Source: Insurance Information Institute / ISO Homeowners Claim Study)*.
* **$15,000–$20,000 Frozen Pipe Bursts:** Aging furnaces locking out during sub-freezing cold snaps freeze residential plumbing *(Source: State Farm Winter Storm Claims Data)*.
* **$89–$150 Unnecessary Truck Rolls:** Homeowners pay $89–$150 service dispatch fees simply to replace a 9V battery or reset a tripped breaker *(Source: HomeAdvisor / Angi 2024 Trade Survey)*.
* **Life Safety Failures:** Residential alarm studies *(CPSC & NFPA)* show homeowners frequently mistake the 30-second end-of-life expiration chirp for a low-battery alert, swap the battery, and leave an expired chemical sensor monitoring lethal gas.

---

### Architecture & The 3-Pillar Engine

```
[Voice Description (`diagnose_from_description`) OR Companion Sensor Audio (`hear_sound`)]
       │
       ▼ (MCP Streamable HTTP `POST /mcp` · JSON-RPC 2.0 · `Mcp-Session-Id`)
[Pillar 1: Hilbert Analytic Envelope A(t) + Hann-Window FFT + `beepdb` Signature Match]
       │
       ▼ (Volatile RAM Zeroing `data.fill(0.0)` · 0 Bytes Audio Written to Disk/SQLite)
[Pillar 2: SQLite Home Graph · Weibull Hazard R(t) + Lumped-Capacitance ODE dT/dt]
       │
       ▼ (Pillar 3: Amazon Bedrock Nova Pro + Amazon Polly Neural TTS + SSE Push)
[Nova Pro 5-Yr TCO Deliberation · Strict Propose -> Confirm · `/events` SSE Banner]
```

#### Pillar 1: Dual-Intake Diagnostics & Ephemeral DSP (<15ms Local Processing)
* **Voice-Native Path (`diagnose_from_description`):** Matches spoken chirp interval (e.g., 30s), chirps per burst, brand, and room location against `beepdb` (20 sourced manufacturer signatures).
* **Companion Sensor Path (`hear_sound` → `diagnose`):** Computes the analytic signal envelope using the Hilbert transform `A(t) = |s(t) + i · H{s(t)}|` and Hann-windowed FFT to extract `(interval_s, peak_frequency_hz, pulse_duration_ms)`. Raw PCM buffers are cleared best-effort in RAM (`data.fill(0.0)`) and never written to disk or SQLite (verified by `test_audio_never_persisted_to_disk_or_db`).

#### Pillar 2: Persistent Mathematical World-Model (Weibull Reliability & Thermodynamics)
Equipment health is modeled via two-parameter Weibull distributions:
```
Reliability: R(t) = exp(-(t / η)^β),   Hazard Rate: h(t) = (β / η) · (t / η)^(β - 1)
```
*(CO Detector: η = 7.0 yr, β = 3.0; HVAC Furnace: η = 15.0 yr, β = 2.2).*

Before issuing freeze alerts, the Proactive Engine models unheated pipe-cavity cooling using Newton's law of cooling:
```
dT_in / dt = -(1 / τ_pipe) · (T_in - T_out) + (Q_furnace / C_thermal)
```
For an unheated pipe zone (`τ_pipe = 16.0 hours`) at `24°F` outdoor ambient, pipe temperature reaches freezing (`32°F`) in `t = -16.0 · ln((32 - 24)/(68 - 24)) = 27.3 hours` when starting from `68°F` (or `21.7 hours` if the cavity starts at `55°F`). Conditioned on `τ_pipe ~ Lognormal(ln(16), 0.3)` and `T_out ~ Normal(24°F, 2.5°F)`, a 5,000-run Monte Carlo simulation yields a **94.1% 48-hour freeze probability** (`P10 = 18.7h`, `P50 = 27.1h`; prior sensitivity: `τ=24h -> 66.0%`, `τ=35h -> 24.6%`).

#### Pillar 3: Amazon Bedrock Specialist Deliberation & Alexa+ Proactivity
* **Amazon Bedrock Nova Pro (`amazon.nova-pro-v1:0`):** Evaluates 5-year repair vs. replace TCO, R-410A refrigerant phaseouts, and SEER savings in **~2.64 seconds** (with transparent `execution_mode` reporting).
* **Strict Propose → Confirm Trust Boundary:** Stages proposals in SQLite; never executes purchases without explicit `confirm_action` confirmation.
* **Server-Sent Events (`/events`) Proactive Push:** Pushes unprompted notifications to the simulator when a replacement delivery arrives or outdoor temperatures drop.

---

### Transparent Validation, Benchmarks & Scope Limits (`22/22` Pytest Gates)

Run `python benchmarks/run_benchmarks.py` and `pytest -v tests/` to reproduce all metrics:

| Benchmark / Test Gate | Measured Result | Honest Scope & Method |
| :--- | :--- | :--- |
| **20-Device Synthetic Cadence Suite** | **95.0% (19/20)** | Multi-burst synthetic WAV regression across all 20 `beepdb` rows (`clip_04` is a 30s Kidde smoke vs CO conservative tie-break). |
| **Physical Smoke Piezos (Bloofrzo CC0)**| **2/2 Calibrated** | Real 1.0s single-chirp recordings (`#819808` at `3,368.1 Hz`, `#819807` at `3,122.3 Hz`); used to calibrate the `±350 Hz` band with user-supplied `30s`/`60s` cadence. |
| **Real Hardware Tone DSP Extraction** | **4/4 Verified** | Real POST beep, appliance beep, buzzer, and alarm recordings verified for accurate Hilbert pulse width and Hann FFT peak extraction. |
| **ESC-50 Domestic Noise Smoke Test** | **6/6 Spec · 6/6 Peak** | `n=12` smoke test on 6 real ESC-50 domestic clips (washer, vacuum, water, knock, steps, clock): `6/6` standalone clips stay `< 0.50` confidence; `6/6` `+15 dB` chirp mixes recover the `3,368 Hz` peak via Hann FFT vs `1/6` for naive global zero-crossing. |
| **Synthetic + ESC-50 Noise Bed** | **90.0% (9/10)** | 10 synthetic cadence clips mixed with real ESC-50 room noise at **+15 dB** and **+6 dB SNR**. |
| **Local DSP + Scrub + SQLite Pipeline** | **13.52 ms** | `9.80 ms` FFT/Hilbert + `0.005 ms` `data.fill(0.0)` + `0.016 ms` `beepdb` + `3.70 ms` SQLite write. |
| **Automated Test Suite** | **22/22 Passing** | Includes `test_mcp_streamable_http_spec_handshake`, `test_simulator_mcp_client_and_cors_session_header`, and `test_audio_never_persisted_to_disk_or_db`. |

---

### Commercial Viability (Illustrative Business Model)

1. **Prime Consumables & Hardware Fulfillment:** Stages 1-click verified replacement proposals (e.g., Kidde KN-COPP-3 or 9V batteries) gated behind user confirmation.
2. **Insurance Carrier Loss-Mitigation Partnerships:** Helps prevent water damage ($12,514 average claim, *III/ISO*) and frozen pipe bursts ($15,000+, *State Farm*) via proactive freeze warnings.
3. **Alexa+ Subscription Retention:** Turns Alexa+ into a proactive home custodian that decodes 3:14 AM alarms and tracks appliance lifecycles.
4. **Automated Warranty Claim Dossiers:** Tracks warranty expiration dates in the Home Graph and drafts claim dossiers for in-warranty failures.

---

## 3. Product Feedback & Friction Logs (Copy & Paste into Devpost Feedback fields)

### Friction Log #1: Gated Alexa+ Preview Access & Lack of an Offline Alexa+ MCP Host Emulator
- **Component / Service:** Alexa+ Track (Simulated Experience Path / MCP `2025-11-25` Integration)
- **Severity:** Medium (Onboarding & Verification Friction for External Developers)
- **Problem Statement:** Because the Alexa+ Developer Preview is gated behind partner allowlisting and identity verification, external builders on the hackathon's permitted simulated-experience path do not have an official local "Alexa+ MCP Host Emulator" to test how the Alexa+ runtime formats `tools/call` requests, renders visual card payloads, or handles proactive server-to-client notifications.
- **Workaround Used:** Built a spec-compliant browser MCP Streamable HTTP JSON-RPC 2.0 client (`client/app.js`) that executes `initialize` → `Mcp-Session-Id` → `notifications/initialized` → `tools/list` → `tools/call` directly against `POST /mcp`, added a voice-native `diagnose_from_description` tool, and verified protocol compliance against the official Python `mcp` SDK in automated tests.
- **Suggested Improvement:** Publish an open-source `@amazon/alexa-plus-mcp-emulator` CLI/web package so developers outside the gated preview can validate MCP Streamable HTTP handshakes, card schemas, and proactive notification hooks locally.

---

### Friction Log #2: MCP Python SDK (`mcp` v2.2.0) `TransportSecurityMiddleware` Blocking Browser CORS Clients (`403 Invalid Origin`)
- **Component / Service:** Model Context Protocol Python SDK (`mcp==2.2.0`, `MCPServer.streamable_http_app`)
- **Severity:** Medium (Breaks Browser-Based MCP Clients Out of the Box)
- **Problem Statement:** When mounting `mcp_server.streamable_http_app(streamable_http_path="/mcp")` inside a FastAPI application for a browser-based simulator, `mcp.server.transport_security.TransportSecurityMiddleware` rejects cross-origin browser requests with `403 Forbidden (Invalid Origin header)` even when FastAPI's `CORSMiddleware` is enabled. Furthermore, browsers hide the `Mcp-Session-Id` header from JavaScript `fetch()` unless `expose_headers=["Mcp-Session-Id", "mcp-session-id"]` is explicitly configured.
- **Workaround Used:** Configured `expose_headers=["Mcp-Session-Id", "mcp-session-id"]` on `CORSMiddleware` and normalized internal ASGI scope headers in `server/main.py` before passing requests to `mcp_app`, verified by `test_simulator_mcp_client_and_cors_session_header`.
- **Suggested Improvement:** Expose an `allowed_origins: list[str]` parameter directly on `MCPServer.streamable_http_app()` and automatically include `Access-Control-Expose-Headers: Mcp-Session-Id` when CORS is enabled.

---

### Friction Log #3: Amazon Bedrock Nova Pro (`amazon.nova-pro-v1:0`) Structured Output Code-Fence Wrapping
- **Component / Service:** Amazon Bedrock Runtime (`amazon.nova-pro-v1:0` / `InvokeModel` API)
- **Severity:** Medium (Reliability Risk in Agent Tooling)
- **Problem Statement:** When prompting Amazon Nova Pro to return strictly valid JSON matching an appliance deliberation schema, the model frequently wraps the JSON response in Markdown code fences (````json { ... } ````) or includes conversational preambles despite system prompts requesting raw JSON only.
- **Workaround Used:** Implemented `parse_json_from_llm()` in `tools/utils.py` (tested in `test_parse_json_from_llm`) to strip code fences and extract the outermost balanced JSON object before calling `json.loads()`.
- **Suggested Improvement:** Support a first-class `response_format={"type": "json_schema", "schema": {...}}` parameter on `InvokeModel` / `Converse` for Amazon Nova models to guarantee schema-valid JSON without regex post-processing.
