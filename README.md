# GENIUS — Graph Engine for Networked Infrastructure Understanding & Service

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP Spec](https://img.shields.io/badge/MCP_Spec-2025--11--25-emerald.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/Bedrock-Amazon_Nova_Pro-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Amazon Polly](https://img.shields.io/badge/Polly-Neural_TTS-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/polly/)
[![CI](https://github.com/patriceai-code/genius/actions/workflows/ci.yml/badge.svg)](https://github.com/patriceai-code/genius/actions/workflows/ci.yml)
[![AWS Hosted Simulator](https://img.shields.io/badge/AWS_Hosted_Simulator-Live_on_S3-FF9900.svg?logo=amazon-aws&logoColor=white)](http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com)

**The Home World Model for the Alexa+ Era**  
*Submitted to the Amazon Developer Hackathon 2026 (Primary Track: Alexa+ | Mini-Challenges: AWS Builder & Open Source)*

[Live AWS Simulator](http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com) · [beepdb Open Source Library](https://github.com/patriceai-code/beepdb) · [Devpost Submission](DEVPOST_SUBMISSION_CLEAN.md) · [Demo Video Script](demo/script.md)

</div>

---

## Executive Summary: What Is Real vs. Simulated

**GENIUS** (*Graph Engine for Networked Infrastructure Understanding & Service*) is a self-hosted **Model Context Protocol (MCP) server** (`spec 2025-11-25`, Streamable HTTP transport at `POST /mcp`) paired with a browser-based **Alexa+ Preview Device Simulator** ([`client/app.js`](client/app.js)).

### What Runs Live in Code
1. **Spec-Compliant MCP Streamable HTTP Client & Server:** [`client/app.js`](client/app.js) connects directly to `POST /mcp` using JSON-RPC 2.0 (`initialize` $\rightarrow$ `Mcp-Session-Id` header $\rightarrow$ `notifications/initialized` $\rightarrow$ `tools/list` $\rightarrow$ `tools/call`) and renders UI cards dynamically from the MCP server's JSON responses.
2. **12 Registered MCP Tools:** Voice-native chirp diagnosis (`diagnose_from_description`), companion-sensor DSP feature extraction (`hear_sound` + `diagnose`), persistent SQLite Home Graph (`list_entities`, `get_home_health`, `register_entity`, `record_incident`), strict `propose_action` $\rightarrow$ `confirm_action` gate, warranty ledger (`check_warranty`, `file_warranty_claim`), and live **Amazon Bedrock Nova Pro** (`amazon.nova-pro-v1:0`) 5-year TCO deliberation (`deliberate_repair`).
3. **Deterministic Signal Processing & Physics:** Hilbert transform amplitude envelope, Hann-windowed FFT, two-parameter Weibull hazard reliability ($R(t)$), and lumped-capacitance building heat-loss simulation ($dT/dt$) with 5,000-run Monte Carlo uncertainty quantification.

### What Is Simulated (Per Alexa+ Track Guidelines)
- Because the Alexa+ Developer Preview is gated and does not stream raw room audio to third-party MCP servers, the primary Alexa+ interaction path is conversational (`diagnose_from_description`), while `hear_sound` represents a companion sensor intake (e.g., mobile app or auxiliary edge microphone).
- Package delivery (`POST /simulate/delivery`), weather drops (`POST /simulate/freeze`), and order fulfillment references (`AMZN-2026-94819-...`) are simulated state triggers used to demonstrate multi-day lifecycles inside a 2-minute evaluation window.
- When the static S3 simulator URL is opened without a local MCP server running, it explicitly displays an amber **`Offline Replay (No MCP Server Connected)`** badge.

---

## 1. Architecture & The 12 MCP Tools

```
                      +----------------------------------+
                      |   ALEXA+ PREVIEW SIMULATOR       |
                      |   (Browser MCP Client app.js)    |
                      +----------------+-----------------+
                                       |
                                       | 1. MCP Streamable HTTP (2025-11-25)
                                       |    POST /mcp (JSON-RPC 2.0 + Mcp-Session-Id)
                                       | 2. SSE Proactive Push (/events)
                                       v
+--------------------------------------+---------------------------------------+
|                              GENIUS MCP SERVER                               |
|                                                                              |
|   +---------------------+   +---------------------+   +------------------+   |
|   | 12 MCP Tools        |   | Acoustic Pipeline   |   | SQLite Graph     |   |
|   | - hear_sound        |   | - Hilbert Envelope  |   | - Entities       |   |
|   | - diagnose          |   | - FFT Peak (3368Hz) |   | - Incidents      |   |
|   | - diagnose_from_... |   | - beepdb Matcher    |   | - Warranties     |   |
|   | - list_entities     |   | - data.fill(0.0)    |   | - Proposals      |   |
|   | - get_home_health   |   +---------------------+   | - Provenance     |   |
|   | - propose_action    |                             +------------------+   |
|   | - confirm_action    |   +---------------------+                          |
|   | - record_incident   |   | Amazon Bedrock      |   +------------------+   |
|   | - register_entity   |   | Nova Pro Engine     |   | Amazon Polly     |   |
|   | - check_warranty    |   | - TCO Deliberation  |   | Neural TTS       |   |
|   | - file_warranty_... |   | - Tag OCR Vision    |   | /api/polly/speak |   |
|   | - deliberate_repair |   +---------------------+   +------------------+   |
|   +---------------------+                                                    |
+------------------------------------------------------------------------------+
```

| # | Tool Name | Key Parameters | Function & Output |
|---|---|---|---|
| 1 | `hear_sound` | `audio_clip_b64`, `location`, `interval_s` | Companion sensor intake. Extracts Hilbert/FFT features in volatile RAM, zeroes buffer (`data.fill(0.0)`), returns features. |
| 2 | `diagnose` | `interval_s`, `peak_freq_hz`, `duration_ms` | Matches features against `beepdb`, logs incident with provenance, stages purchase/remedy proposal. |
| 3 | `diagnose_from_description` | `interval_s`, `chirps_per_burst`, `brand`, `device_hint` | **Voice-native Alexa+ path:** Matches spoken chirp cadence, burst count, and brand hints against `beepdb` without raw audio. |
| 4 | `list_entities` | `lifecycle_filter` | Queries the Home Graph hardware registry with verified provenance tags and Weibull reliability scores. |
| 5 | `get_home_health` | none | Computes composite 0–100 health score, healthy/aging/EOL counts, and MCP Apps card payload. |
| 6 | `propose_action` | `kind`, `title`, `entity_id` | **Strict architectural gate:** Stages structured proposal in SQLite. Never mutates external state. |
| 7 | `confirm_action` | `proposal_id`, `confirmed` | Authorization mutation gate. Marks proposal confirmed and returns dynamic order reference only after explicit user approval. |
| 8 | `record_incident` | `entity_id`, `description`, `severity` | Appends anomaly record to the persistent SQLite Home Graph ledger. |
| 9 | `register_entity` | `brand`, `model`, `location`, `year` | Day 0 onboarding. Registers equipment specifications (or parses nameplate image via Bedrock Nova Pro) and seeds warranty policies. |
| 10 | `check_warranty` | `entity_id` | Inspects policy coverage dates, active/expired status, and manufacturer replacement terms. |
| 11 | `file_warranty_claim` | `entity_id`, `reason` | Assembles manufacturer replacement claim dossier for devices that fail within warranty. |
| 12 | `deliberate_repair` | `entity_id`, `issue_description` | **AWS Builder:** Invokes Amazon Bedrock Nova Pro (`amazon.nova-pro-v1:0`) for 5-year repair-vs-replace TCO analysis. |

---

## 2. Signal Processing, Reliability Priors & Thermal Physics

### A. Acoustic Feature Extraction (`audio/features.py` & `audio/ephemeral.py`)
1. **Analytic Signal Envelope (Hilbert Transform):** Computes $A(t) = |s(t) + i \cdot \mathcal{H}\{s(t)\}|$ to measure continuous pulse width ($\text{ms}$) across oscillating $3\text{ kHz}+$ piezo square waves without zero-crossing dropouts.
2. **Spectral Peak Extraction (Hann-Windowed FFT):** Extracts dominant frequency $f_{\text{peak}}$ above $400\text{ Hz}$. Physical smoke detector piezo recordings (Bloofrzo CC0 `#819808` at $3,368.1\text{ Hz}$ and `#819807` at $3,122.3\text{ Hz}$ vs $3,200\text{ Hz}$ nominal manual spec) motivated our calibrated $\pm 350\text{ Hz}$ tolerance window in `beepdb`.
3. **Zero Disk Persistence:** Raw audio is never written to disk, logs, or SQLite (verified by `test_audio_never_persisted_to_disk_or_db`), and in-memory PCM arrays are cleared best-effort via `data.fill(0.0)`.

### B. Continuous Reliability Priors (`graph/store.py`)
Equipment lifecycle degradation is modeled using two-parameter Weibull priors:

$$R(t) = \exp\left(-\left(\frac{t}{\eta}\right)^\beta\right), \quad h(t) = \frac{\beta}{\eta} \left(\frac{t}{\eta}\right)^{\beta - 1}$$

- **CO Detectors:** $\eta = 7.0\text{ yr}, \beta = 3.0$ (electrochemical electrolyte dry-out)
- **Smoke Detectors:** $\eta = 10.0\text{ yr}, \beta = 2.5$ (optical chamber degradation)
- **HVAC Furnaces:** $\eta = 15.0\text{ yr}, \beta = 2.2$ (heat exchanger thermal fatigue)
- **Water Heaters:** $\eta = 10.0\text{ yr}, \beta = 2.0$ (sacrificial anode depletion)

### C. Lumped-Capacitance Pipe Freeze Model (`proactive/engine.py`)
Before issuing freeze warnings, the Proactive Engine evaluates unheated pipe-cavity cooling ($Q_{\text{furnace}} = 0$):

$$T_{\text{zone}}(t) = T_{\text{out}} + \big(T_{\text{zone}}(0) - T_{\text{out}}\big) \cdot e^{-t / \tau_{\text{pipe}}}$$

- **Deterministic Trajectory ($\tau_{\text{pipe}} = 16.0\text{ h}$, $T_{\text{out}} = 24^\circ\text{F}$):** Starting from $68^\circ\text{F}$ indoor setpoint, the pipe zone reaches $32^\circ\text{F}$ in $t = -16.0 \cdot \ln(8/44) = \mathbf{27.3\text{ hours}}$ (or **$21.7\text{ hours}$** if the uninsulated cavity starts cooler at $55^\circ\text{F}$; whole-house envelope $\tau = 35\text{ h}$ reaches $32^\circ\text{F}$ in $59.7\text{ hours}$).
- **Conditioned Monte Carlo ($N = 5,000$, seed 42):** Under $\tau_{\text{pipe}} \sim \text{Lognormal}(\ln(16), 0.3)$ and $T_{\text{out}} \sim \mathcal{N}(24^\circ\text{F}, 2.5^\circ\text{F})$, $P(T_{\text{pipe}} \le 32^\circ\text{F} \text{ within } 48\text{ h}) = \mathbf{94.1\%}$ ($P_{10} = 18.7\text{ h}$, $P_{50} = 27.1\text{ h}$; sensitivity across alternative priors: $\tau = 24\text{ h} \rightarrow 66.0\%$, $\tau = 35\text{ h} \rightarrow 24.6\%$).

---

## 3. Transparent Benchmarks & Automated Test Suite (`22/22` Passing)

Run `python benchmarks/run_benchmarks.py` (writes receipt to [`benchmarks/latest_benchmark_receipt.json`](benchmarks/latest_benchmark_receipt.json)) and `pytest -v tests/` to reproduce all metrics:

| Benchmark / Verification Gate | Measured Result | Honest Scope & Method |
| :--- | :--- | :--- |
| **20-Device Synthetic Cadence Suite** | **95.0% (19/20)** | Multi-burst synthetic WAV regression across all 20 `beepdb` rows (`clip_04` Kidde smoke `3,100 Hz` vs Kidde CO `3,200 Hz` at 30s cadence resolves to higher critical severity). |
| **Physical Smoke Piezos (Bloofrzo CC0)** | **2/2 Calibrated** | Real 1.0s single-chirp recordings (`#819808` at `3,368.1 Hz`, `#819807` at `3,122.3 Hz`); used to calibrate the `±350 Hz` band with user-supplied `30s`/`60s` cadence. |
| **Real Hardware Tone DSP Extraction** | **4/4 Verified** | Real PC POST beep, microwave beep, buzzer, and alarm recordings verified for accurate Hilbert pulse width and Hann FFT peak extraction. |
| **ESC-50 Domestic Noise Smoke Test** | **6/6 Spec · 6/6 Peak** | `n=12` smoke test on 6 real ESC-50 domestic clips (washer, vacuum, water, knock, steps, clock): `6/6` standalone clips stay `< 0.50` confidence; `6/6` `+15 dB` chirp mixes recover the `3,368 Hz` peak via Hann FFT vs `1/6` for naive global zero-crossing. |
| **Synthetic + ESC-50 Noise Bed** | **90.0% (9/10)** | 10 synthetic cadence clips mixed with real ESC-50 domestic room noise at **+15 dB** and **+6 dB SNR**. |
| **Local DSP + Scrub + SQLite Pipeline** | **~13.5 ms** | `~9.80 ms` FFT/Hilbert + `0.005 ms` `data.fill(0.0)` + `0.016 ms` `beepdb` lookup + `~3.70 ms` SQLite write. |
| **Automated Pytest Suite** | **22/22 Passing** | Includes `test_mcp_streamable_http_spec_handshake`, `test_simulator_mcp_client_and_cors_session_header`, and `test_audio_never_persisted_to_disk_or_db`. |

```powershell
pytest -v tests/
python benchmarks/run_benchmarks.py
```

---

## 4. Quickstart & Cloud Deployment

### Option 1: Local Python Environment (Full Live MCP Server + Simulator)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Launch FastAPI + MCP Streamable HTTP Server
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
Open **`http://127.0.0.1:8000/client/index.html`**. The simulator header will display a green **`Live MCP Session (...) · Spec 2025-11-25`** badge confirming an active JSON-RPC 2.0 session over `POST /mcp`.

### Option 2: Docker Compose
```bash
docker compose up --build
```

### Option 3: Static AWS S3 Simulator Preview
- **URL:** [http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com](http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com)
- Displays **`Offline Replay (No MCP Server Connected)`** until pointed at a running MCP server via the **⚙️ Server URL** button.

---

## 5. Architectural Decision Records (ADRs)

- **ADR 001 (Proactive Push Transport):** Uses Server-Sent Events (`/events`) to push unprompted notifications to the simulator alongside a dormant MCP notification stub (`proactive/transports/mcp_push.py`).
- **ADR 002 (Smart Home API Deferral):** Defers legacy OAuth Smart Home skill linking in favor of self-hosted MCP Streamable HTTP (`2025-11-25`).
- **ADR 003 (Simulator-Only Demo Path):** Because Alexa+ builder tooling is gated, the demo runs on the labeled **"ALEXA+ PREVIEW DEVICE SIMULATOR"** (`client/app.js`), which acts as a real MCP Streamable HTTP client calling `POST /mcp`. Echo hardware integration is not claimed.

---

## 6. Licensing & Attributions

- **Code:** [MIT License](LICENSE) (both `genius` and standalone [`beepdb`](https://github.com/patriceai-code/beepdb)).
- **Data & Audio Corpus:** [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) and CC0 Public Domain. Full attributions in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
