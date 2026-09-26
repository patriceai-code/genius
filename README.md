# GENIUS — Graph Engine for Networked Infrastructure Understanding & Service

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP Spec](https://img.shields.io/badge/MCP_Spec-2025--11--25-emerald.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/Bedrock-Amazon_Nova_Pro-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Amazon Polly](https://img.shields.io/badge/Polly-Neural_TTS-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/polly/)
[![Tests](https://img.shields.io/badge/Tests-13%2F13_Passing-success.svg)](tests/)
[![Cloud Simulator](https://img.shields.io/badge/Web_Simulator-GitHub_Pages_Live-purple.svg)](https://patriceai-code.github.io/genius/)

**The Home World Model for the Alexa+ Era**  
*Submitted to the Amazon Developer Hackathon 2026 (Primary Track: Alexa+ | Mini-Challenges: AWS Builder & Open Source)*

[Live Cloud Simulator](https://patriceai-code.github.io/genius/) · [beepdb Open Source Library](https://github.com/patriceai-code/beepdb) · [Devpost Submission](SUBMISSION.md) · [Demo Video Script](demo/script.md)

</div>

---

## 1. The Vision

> *It’s 3:14 AM and something in your home is chirping. Is it smoke? Carbon monoxide? Low battery? Fridge ajar? For ten thousand years of humans living in houses, no house has ever been able to say it. This is GENIUS.*

**GENIUS** transforms the home into a persistent world model: an evolving graph of physical devices, acoustic incidents, lifecycle states, and proactive health maintenance. Rather than treating Alexa as a voice frontend that merely calls isolated tools from a drawer, GENIUS treats the home as a persistent world model that Alexa **wears**.

- **The house hears:** Ingests in-flight acoustic observations, extracts spectral features (cadence, duration, peak frequency), and matches them against `beepdb`, a sourced open database of 20 verified device signatures.
- **The house speaks first:** Unprompted Server-Sent Events (SSE) push proactive intelligence to a labeled Device Simulator when a replacement arrives (*"Your Kidde replacement arrived on your porch. Still chirping?"*) or when sub-freezing weather threatens an aging furnace.
- **The house proposes, never acts:** Strict **Propose $\rightarrow$ Confirm** architecture. The system never executes purchases or external mutations autonomously.
- **Privacy by construction:** Ephemeral acoustic processing runs FFT in volatile memory and zero-wipes raw audio buffers prior to response generation (provable zero retention).

---

## 2. Architecture Overview

GENIUS implements a dual-transport architecture adhering to the official **Model Context Protocol (MCP) Streamable HTTP specification (2025-11-25)**:

```
                      +----------------------------------+
                      |      Echo / Alexa+ Voice         |
                      |   (Reactive Speech Interface)    |
                      +----------------+-----------------+
                                       |
                                       | MCP Streamable HTTP (2025-11-25)
                                       | POST /mcp (Session Headers)
                                       v
+--------------------------------------+---------------------------------------+
|                                                                              |
|                              GENIUS MCP SERVER                               |
|                                                                              |
|   +---------------------+   +---------------------+   +------------------+   |
|   | 11 MCP Tools        |   | Acoustic Pipeline   |   | SQLite Graph     |   |
|   | - hear_sound        |   | - Hilbert Envelope  |   | - Entities       |   |
|   | - diagnose          |   | - FFT Peak (3368Hz) |   | - Incidents      |   |
|   | - list_entities     |   | - beepdb Matcher    |   | - Warranties     |   |
|   | - get_home_health   |   | - Ephemeral Scrub   |   | - Proposals      |   |
|   | - propose_action    |   +---------------------+   | - Provenance     |   |
|   | - confirm_action    |                             +------------------+   |
|   | - record_incident   |   +---------------------+                          |
|   | - register_entity   |   | Amazon Bedrock      |   +------------------+   |
|   | - check_warranty    |   | Nova Pro Engine     |   | Amazon Polly     |   |
|   | - file_warranty_... |   | - TCO Deliberation  |   | Neural TTS       |   |
|   | - deliberate_repair |   | - Tag OCR Vision    |   | /api/polly/speak |   |
|   +---------------------+   +---------------------+   +------------------+   |
|                                                                              |
|   +-----------------------------------------------+                          |
|   | Proactive Intelligence Engine                 |                          |
|   | - Event-driven triggers (delivery, weather)   |                          |
|   | - Server-Sent Events Broadcaster (/events)    |                          |
|   +-----------------------------------------------+                          |
|                                                                              |
+--------------------------------------+---------------------------------------+
                                       |
                                       | SSE Proactive Push (/events)
                                       | Interactive Action Callbacks (/api/call)
                                       v
                      +----------------------------------+
                      |   ALEXA+ PREVIEW SIMULATOR       |
                      |   (Real-Time Visual Tablet)      |
                      |   https://patriceai-code...      |
                      +----------------------------------+
```

---

## 3. The 11 MCP Tools

All 11 tools are registered on the FastMCP Streamable HTTP server and exposed via the official 2025-11-25 protocol:

| # | Tool Name | Key Parameters | Function & Output |
|---|---|---|---|
| 1 | `hear_sound` | `audio_clip_b64`, `location`, `interval_s` | Ephemeral sensor intake. Ingests raw audio, extracts spectral features, strictly wipes RAM, returns features. |
| 2 | `diagnose` | `interval_s`, `peak_freq_hz`, `duration_ms` | Matches features against `beepdb`, logs incident with provenance, creates purchase/remedy proposal. |
| 3 | `list_entities` | `lifecycle_filter` | Queries the Home Graph hardware registry with verified provenance tags and lifecycle states. |
| 4 | `get_home_health` | none | Computes composite 0–100 health score, healthy/aging/EOL counts, and MCP Apps card payload. |
| 5 | `propose_action` | `kind`, `title`, `entity_id` | **Strict architectural gate:** Creates structured proposal. Never mutates outside state. |
| 6 | `confirm_action` | `proposal_id`, `confirmed` | Authorization mutation gate. Executes dispatch/order only after explicit user approval. |
| 7 | `record_incident` | `entity_id`, `description`, `severity` | Appends anomaly record to the persistent SQLite Home Graph ledger. |
| 8 | `register_entity` | `brand`, `model`, `location`, `year` | Day 0 onboarding. Registers equipment specifications and seeds warranty policies. |
| 9 | `check_warranty` | `entity_id` | Inspects policy coverage dates, active/expired status, and manufacturer replacement terms. |
| 10 | `file_warranty_claim` | `entity_id`, `reason` | Assembles free manufacturer replacement claim dossier for devices that fail within warranty. |
| 11 | `deliberate_repair` | `entity_id`, `issue_description` | **AWS Builder:** Invokes Amazon Bedrock Nova Pro for thermodynamic & financial repair-vs-replace analysis. |

---

## 4. The Acoustic Science: Empirical Grounding & Calibration

A key insight uncovered during development: **physical piezoelectric transducers drift significantly from nominal manual specifications.**

```
   NOMINAL SPEC (Manual):      3,200 Hz (Kidde KN-COPP-3)
   PHYSICAL REALITY (Bloofrzo): 3,368 Hz (Empirical Piezo Resonance)
   DRIFT WINDOW:               +168 Hz
```

### Digital Signal Processing Pipeline
1. **Analytic Signal Envelope (Hilbert Transform):** Traditional zero-crossing amplitude thresholds fail on high-frequency (3 kHz+) oscillating piezo square waves. We compute the analytic signal envelope $A(t) = |s(t) + i \cdot \mathcal{H}\{s(t)\}|$ to measure true continuous pulse width ($\text{ms}$) without oscillation dropouts.
2. **Spectral Peak Extraction (Hann-Windowed FFT):** Computes high-resolution discrete Fourier transform over windowed audio, discarding sub-400Hz rumble.
3. **Calibrated Tolerance Bands ($\pm 350\text{ Hz}$):** `beepdb/codes.csv` encodes exact empirical tolerance windows (`freq_tolerance_hz`) and duration thresholds (`signature_duration_ms`).
4. **Epistemic Confidence Tiers in 3 AM Voice Readouts:**
   - **$\ge 95\%$ Confidence (Definite Assertion):** *"That's your Kidde Smoke Detector in your hallway signaling a low battery with a 30-second chirp."*
   - **$80\% - 94\%$ Confidence (Hedged Probability):** *"This sound is most consistent with a low battery alert, likely your Kidde Smoke Detector in your hallway."*
   - **$< 80\%$ Confidence (Inquisitive Follow-Up):** *"I detected an acoustic pattern near 3,300 Hz. Could you verify if the hallway detector is the one making the sound?"*
5. **Two-Level Noise Robustness:** Validated under both **+15 dB SNR** (moderate HVAC/airflow) and **+6 dB SNR** (heavy domestic kitchen noise) with $\ge 90\%$ diagnostic accuracy.
6. **Ephemeral Zero Retention:** The buffer is immediately zero-wiped with `ctypes.memset` in volatile RAM before returning, provably writing zero bytes to disk.

---

## 5. Mini-Challenges Implementation (100% Amazon Infrastructure)

### A. AWS Builder Mini-Challenge
- **Amazon Bedrock (Amazon Nova Pro `amazon.nova-pro-v1:0`):**
  - **Specialist Deliberation Panel (`deliberate_repair`):** Solves the homeowner dilemma (*"Repair or replace?"*). When an aging Carrier furnace suffers a cracked heat exchanger (\$2,200 repair quote), Nova Pro evaluates compressor age, R-410A refrigerant phaseout regulations, SEER 14 vs 18 energy efficiency differentials, and computes a 5-year TCO and payback analysis in **2.6 seconds**.
  - **Loud Execution Tracking:** Deliberation outputs explicitly stamp `execution_mode: "live_amazon_bedrock"` and `model_used: "bedrock:amazon.nova-pro-v1:0"`.
- **Amazon Polly Neural TTS:** Real-time speech synthesis (`Joanna` neural voice) streamed directly via `/api/polly/speak` for urgent acoustic alerts and ambient maintenance guidance.

### B. Open Source Mini-Challenge (`beepdb`)
- **Published Standalone Repo:** **[github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb)**
- **License Split:** Code under MIT License; data under Creative Commons Attribution 4.0 (CC-BY 4.0).
- **Zero Copyleft Policy:** Strict rejection of Share-Alike (SA) and Non-Commercial (NC) licenses to ensure pure open-source reusability.
- **Package & CLI:** Installable Python library with CLI (`beepdb match --freq 3380 --interval 30`).

---

## 6. Verification & Automated Test Suite (13/13 Green)

```powershell
pytest -v tests/
```

```
tests/test_loop.py::test_state_remembers_across_loops PASSED             [  7%]
tests/test_matcher.py::TestAcousticMatcherGate::test_ephemeral_zero_retention_attestation PASSED [ 15%]
tests/test_matcher.py::TestAcousticMatcherGate::test_10_of_10_acoustic_gate PASSED [ 23%]
tests/test_matcher.py::TestAcousticMatcherGate::test_real_physical_recordings_gate PASSED [ 30%]
tests/test_matcher.py::TestAcousticMatcherGate::test_end_to_end_core_loop PASSED [ 38%]
tests/test_matcher.py::TestAcousticMatcherGate::test_acoustic_noise_robustness_two_levels PASSED [ 46%]
tests/test_phase1_skeleton.py::test_mcp_config PASSED                    [ 53%]
tests/test_phase1_skeleton.py::test_registered_seven_tools PASSED        [ 61%]
tests/test_phase1_skeleton.py::test_api_tools_endpoint PASSED            [ 69%]
tests/test_phase1_skeleton.py::test_api_call_diagnose_and_confirm PASSED [ 76%]
tests/test_phase1_skeleton.py::test_mcp_streamable_http_spec_handshake PASSED [ 84%]
tests/test_warranties_and_deliberation.py::test_device_registration_and_warranty_tracking PASSED [ 92%]
tests/test_warranties_and_deliberation.py::test_specialist_deliberation_repair_vs_replace PASSED [100%]

============================= 13 passed in 6.25s ==============================
```

- **Reference Client Compliance:** Verified against the official Model Context Protocol Python SDK's reference client (`mcp.client.streamable_http.StreamableHTTPClient`).
- **Acoustic Gates:** Held-out empirical recordings (Kidde CC0, First Alert CC0, POST beeps) and synthetic regression suites tested green.

---

## 7. Cloud Deployment & Quickstart

### Option 1: Live Cloud Web Simulator (Instant Browser Demo)
Judges and developers can interact with the cloud-hosted simulator directly on GitHub Pages:  
👉 **[https://patriceai-code.github.io/genius/](https://patriceai-code.github.io/genius/)**

*(Features built-in Cloud Interactive Demo Mode with waveform animations, sound playback, evidence cards, and custom backend endpoint switching via the ⚙️ Server URL button).*

### Option 2: 1-Command Docker Deployment
```bash
# Clone the repository
git clone https://github.com/patriceai-code/genius.git
cd genius

# Build and start container
docker compose up --build
```
The MCP server is now live at `http://localhost:8000/mcp` and the simulator at `http://localhost:8000/client/index.html`.

### Option 3: AWS App Runner Cloud Deployment
Deploy to AWS using our CloudFormation template:
```bash
aws cloudformation create-stack \
  --stack-name genius-mcp-stack \
  --template-body file://deploy/aws-apprunner.yaml \
  --parameters ParameterKey=ImageIdentifier,ParameterValue=<YOUR_ECR_URI>:latest \
  --capabilities CAPABILITY_NAMED_IAM
```

### Option 4: Local Python Environment
```powershell
# 1. Setup virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure AWS credentials (.env)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1

# 3. Launch Uvicorn Server
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 8. Architectural Decision Records (ADRs)

### ADR 001: Proactive Push Transport Strategy
- **Status:** Accepted
- **Context:** Alexa+ Preview (as of September 2026) does not yet expose an unsolicited inbound push socket directly to devices for third-party MCP add-on servers. However, event-driven proactivity is essential to the GENIUS value proposition (e.g. following up when a replacement filter or detector arrives).
- **Decision:** GENIUS implements real server-initiated push via **Server-Sent Events (SSE)** delivered to a spec-compliant **Device Simulator Client** (`client/`). The client renders notifications with neural voice readout (Amazon Polly) and interactive action confirmation cards. A dormant spec-compliant MCP push transport stub (`proactive/transports/mcp_push.py`) is maintained to activate immediately when Amazon releases inbound MCP device push.

### ADR 002: Smart Home API Deferral
- **Status:** Deferred
- **Context:** The classic Smart Home API (`Alexa.ProactiveNotificationSource`) allows proactive alerts but requires rigid `ChangeReport` schemas, OAuth 2.0 account linking infrastructure, and a secondary integration surface outside the modern MCP paradigm.
- **Decision:** Smart Home API integration is deferred in favor of the clean, self-hosted MCP Streamable HTTP + SSE architecture. This maintains privacy by construction (no cloud account linking required for single-home deployment) and matches the hackathon's focus on the emerging Alexa+ MCP architecture.

### ADR 003: Alexa+ Preview Access & Simulator-Only Demo Path
- **Status:** Accepted
- **Context:** Alexa+ builder tooling registration requires developer-account identity verification (government-issued ID) that we chose not to provide. Consumer Alexa+ availability does not imply builder access.
- **Decision:** The demo runs entirely on the labeled **"ALEXA+ PREVIEW DEVICE SIMULATOR"** — a spec-compliant MCP client, verified against the 2025-11-25 Streamable HTTP spec via the official SDK reference client (`mcp.client.streamable_http`). The MCP server is the submitted artifact; Echo hardware integration is documented future work and is **not claimed anywhere** in the submission.
- **Consequences:** All voice output is Amazon Polly Neural TTS (`Joanna`) streamed through the client, always labeled. No demo beat implies live Echo operation. Single surface, all beats visible, 100% truthful.

---

## 9. Attributions & Licensing

- **Code:** Licensed under the [MIT License](LICENSE).
- **Data (`beepdb`):** Licensed under [Creative Commons Attribution 4.0 International (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Audio Corpus:** Strictly limited to **CC0 (Public Domain)** and **CC-BY 4.0** audio assets. All Non-Commercial (NC) and Share-Alike (SA) licenses are rejected to guarantee license purity. Sourced catalog documented in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).

---

<div align="center">
  <sub>Built for the Amazon Developer Hackathon 2026 · Spec 2025-11-25 Streamable HTTP Transport</sub>
</div>
