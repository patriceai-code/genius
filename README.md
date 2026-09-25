# GENIUS — Graph Engine for Networked Infrastructure Understanding & Service

> *Every place has a genius. Yours finally speaks.*

GENIUS is a self-hosted Model Context Protocol (MCP) server adhering to the **2025-11-25 Streamable HTTP transport spec** for the **Alexa+ Track** of the [Amazon Developer Hackathon 2026](https://amazonappdev2026.devpost.com/). It equips a home with a persistent world model: an evolving graph of its devices, acoustic incidents, lifecycle states, and proactive health maintenance.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Echo / Alexa+ Preview    |
                      |  (Voice Reactive Interface) |
                      +--------------+--------------+
                                     |
                                     | MCP Streamable HTTP (2025-11-25)
                                     v
+------------------------------------+------------------------------------+
|                                                                         |
|                          GENIUS MCP Server                              |
|                                                                         |
|   +-------------------+    +--------------------+    +--------------+   |
|   | 7 MCP Tools       |    | Acoustic Pipeline  |    | Home Graph   |   |
|   | (hear_sound,      |    | (Ephemeral FFT,    |    | (SQLite      |   |
|   |  diagnose,        |    |  Cadence & Peak,   |    |  Entities &  |   |
|   |  propose_action...)    |  beepdb Matcher)   |    |  Incidents)  |   |
|   +-------------------+    +--------------------+    +--------------+   |
|                                                                         |
|   +-------------------+    +----------------------------------------+   |
|   | Proactive Engine  |    | Server-Sent Events (SSE) Transport     |   |
|   | (State triggers)  |--->| /events                                |   |
|   +-------------------+    +----------------------------------------+   |
+------------------------------------+------------------------------------+
                                     |
                                     | SSE Push
                                     v
                      +-----------------------------+
                      |   GENIUS Device Simulator   |
                      |  (Real-Time Visual Tablet)  |
                      +-----------------------------+
```

---

## Architectural Decision Records (ADRs)

### ADR 001: Proactive Push Transport Strategy
- **Status:** Accepted
- **Context:** Alexa+ Preview (as of September 2026) does not yet expose an unsolicited inbound push socket directly to devices for third-party MCP add-on servers. However, event-driven proactivity is essential to the GENIUS value proposition (e.g. following up when a replacement filter or detector arrives).
- **Decision:** GENIUS implements real server-initiated push via **Server-Sent Events (SSE)** delivered to a spec-compliant **Device Simulator Client** (`client/`). The client renders notifications with neural voice readout (Amazon Polly) and interactive action confirmation cards. A dormant spec-compliant MCP push transport stub (`proactive/transports/mcp_push.py`) is maintained to activate immediately when Amazon releases inbound MCP device push.

### ADR 002: Smart Home API Deferral
- **Status:** Deferred
- **Context:** The classic Smart Home API (`Alexa.ProactiveNotificationSource`) allows proactive alerts but requires rigid `ChangeReport` schemas, OAuth 2.0 account linking infrastructure, and a secondary integration surface outside the modern MCP paradigm.
- **Decision:** Smart Home API integration is deferred in favor of the clean, self-hosted MCP Streamable HTTP + SSE architecture. This maintains privacy by construction (no cloud account linking required for single-home deployment) and matches the hackathon's focus on the emerging Alexa+ MCP architecture.

### ADR 003: Alexa+ Preview Access, Regional Gating & Dual-Device Staging
- **Status:** Accepted
- **Context:** The Alexa+ Developer Preview Toolkit / Add-on Agent Skill CLI is currently invitation-gated and region-restricted (US-East preview cohort; consumer UK Alexa+ rollout scheduled Mar 2026 does not grant developer preview CLI credentials). 
- **Decision:** We execute a two-device staging architecture adhering strictly to hackathon submission rules:
  1. **Reactive Voice Surface:** Live Amazon Echo hardware with Alexa+ voice handling user queries (*"Alexa, what's that sound?"*).
  2. **Proactive Multimodal Surface:** The labeled **"ALEXA+ PREVIEW DEVICE SIMULATOR"** (`client/`) receiving real-time Server-Sent Events from the production MCP server.
  3. **Protocol Compliance:** Verified against the official Model Context Protocol Streamable HTTP specification (2025-11-25) using both native unit/integration test suites and the official `StreamableHTTPClient` SDK.
  4. **Transparency:** Simulator usage is explicitly disclosed in the video title card, UI headers, Devpost documentation, and Community Forum submissions.

---

## Core Loop & Principles

1. **The Core Loop:**
   $$\text{Sound} \longrightarrow \text{Diagnosis} \longrightarrow \text{Graph State} \longrightarrow \text{Proactive Event} \longrightarrow \text{Confirmed Action}$$
2. **Ephemeral by Design:** Acoustic input is processed strictly in-flight. Spectral features (chirp interval, duration, peak frequency) are extracted in volatile memory, and raw audio buffers are immediately discarded before the response returns.
3. **Propose $\rightarrow$ Confirm:** The system never executes external mutations (orders, dispatches, mode switches) autonomously. It creates structured proposals that require explicit user confirmation.

---

## 11 Spec-Compliant MCP Tools

| Tool | Parameters | Description |
|---|---|---|
| `hear_sound` | `audio_data` or `cadence_profile` | Ingests acoustic observation, analyzes in-flight, returns spectral features |
| `diagnose` | `acoustic_features` | Matches against `beepdb`, records incident, generates proposal |
| `list_entities` | `filter_status` | Returns registered home devices and physical equipment |
| `get_home_health` | none | Generates real-time home scorecard & MCP Apps card payload |
| `propose_action` | `action_type`, `params` | Creates a structured proposal requiring explicit confirmation |
| `confirm_action` | `proposal_id` | User-authorized execution mutation gate |
| `record_incident` | `entity_id`, `incident_type`, `details` | Appends verified incident to the Home Graph ledger |
| `register_entity` | `name`, `model`, `category`, `image_base64` | Day 0 onboarding via manual input or Bedrock Claude 3.5 tag vision |
| `check_warranty` | `entity_id` | Verifies active warranty status, coverage, and expiration |
| `file_warranty_claim` | `entity_id`, `incident_id` | Generates free manufacturer warranty replacement dossier |
| `deliberate_repair` | `entity_id`, `issue_description` | AWS Bedrock engineering panel: Repair vs. Replace payback & 5-yr TCO |

---

## Mini-Challenges

### 1. AWS Builder Mini-Challenge
- **Amazon Bedrock (Anthropic Claude 3.5 Sonnet):**
  - **Specialist Deliberation Panel:** Solves the homeowner dilemma ("Repair or replace?"), computing diagnostic confidence, payback period, and 5-year total cost of ownership.
  - **Multimodal Day 0 Tag Vision:** Automatically extracts model numbers, serials, and dates from appliance tags to register manufacturer warranties.
  - **Manual Ingestion Engine:** Parses manufacturer PDFs into structured `beepdb` acoustic records.
- **Amazon Polly Neural TTS:** Real-time speech synthesis delivering natural voice alerts to the Alexa+ Device Simulator.

### 2. Open Source Mini-Challenge (`beepdb`)
- **Standalone Package & Database:** Published separately under the MIT License at **[github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb)**.
- **Data Attributions:** 20 verified device acoustic signatures mapped with exact URLs to manufacturer safety manuals (CC-BY 4.0 data attribution).
- **Acoustic Verification Methodology:** Cadence intervals are cited directly from official manufacturer safety manuals; acoustic frequencies are modeled on nominal piezo component resonance with calibrated tolerance bands (`freq_tolerance_hz`), with physical recording verification status explicitly cataloged.
- **Python Library & CLI:** `pip install beepdb` ready, featuring in-memory matching and tolerance-aware acoustic classification.

---

## Verification & Testing

GENIUS includes a complete automated test suite verifying every component against both physical recordings and calibrated synthetic clips:

```powershell
pytest -v tests/
```

- **11/11 tests passing:**
  - **Empirical Physical Audio Gate:** Evaluates real physical recordings of smoke detectors (Freesound #819808 / #819807, Bloofrzo, CC0) confirming real piezo resonance (3321–3368 Hz) matches verified signatures.
  - **Synthetic Regression Plumbing Gate:** Verifies DSP feature extraction across 10 diverse device categories (smoke, CO, fridge, leak, UPS, furnace).
  - **In-flight Ephemeral Zero-Retention Attestation:** Verifies RAM zero-wiping (176k+ bytes scrubbed) with zero audio stored to disk.
  - **Full Core Loop Integration:** (hear $\rightarrow$ diagnose $\rightarrow$ graph $\rightarrow$ proposal $\rightarrow$ confirm).
  - **Proactive Push & Amazon Bedrock:** Server-Sent Events push engine, warranty tracking, and Bedrock deliberation.


---

## Quickstart

```powershell
# 1. Clone repository
git clone https://github.com/patriceai-code/genius.git
cd genius

# 2. Setup virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Fill in AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

# 4. Start the MCP Server & Web Simulator
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000

# 5. Open Simulator in browser
# http://127.0.0.1:8000/client/index.html
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Audio clips and dataset sources adhere to the CC0 / CC-BY protocol detailed in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
BeepDB is licensed under MIT and CC-BY 4.0 at [github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb).

