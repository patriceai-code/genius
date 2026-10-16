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

[Live AWS Simulator](http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com) · [beepdb Open Source Library](https://github.com/patriceai-code/beepdb) · [Devpost Submission](SUBMISSION.md) · [Demo Video Script](demo/script.md)

</div>

---

## 1. The Vision

> *It’s 3:14 AM and something in your home is chirping. Is it smoke? Carbon monoxide? Low battery? Fridge ajar? For ten thousand years of humans living in houses, no house has ever been able to say it. This is GENIUS.*

**GENIUS** transforms the home into a persistent world model: an evolving graph of physical devices, acoustic incidents, continuous reliability degradation, and proactive health maintenance. Rather than treating Alexa as a voice frontend that merely calls isolated tools from a drawer, GENIUS treats the home as a persistent world model that Alexa **wears**.

- **The house hears:** Ingests in-flight acoustic observations, extracts spectral features (cadence, duration, peak frequency), and matches them against `beepdb`, a sourced open database of 20 verified device signatures.
- **The house predicts:** Evaluates physical state using continuous Weibull reliability distributions ($R(t)$) and simulates 48-hour thermodynamic building freeze counterfactuals before taking action.
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
|   | 12 MCP Tools        |   | Acoustic Pipeline   |   | SQLite Graph     |   |
|   | - hear_sound        |   | - Hilbert Envelope  |   | - Entities       |   |
|   | - diagnose          |   | - FFT Peak (3368Hz) |   | - Incidents      |   |
|   | - diagnose_from_... |   | - beepdb Matcher    |   | - Warranties     |   |
|   | - list_entities     |   | - Ephemeral Scrub   |   | - Proposals      |   |
|   | - get_home_health   |   +---------------------+   | - Provenance     |   |
|   | - propose_action    |                             +------------------+   |
|   | - confirm_action    |   +---------------------+                          |
|   | - record_incident   |   | Amazon Bedrock      |   +------------------+   |
|   | - register_entity   |   | Nova Pro Engine     |   | Amazon Polly     |   |
|   | - check_warranty    |   | - TCO Deliberation  |   | Neural TTS       |   |
|   | - file_warranty_... |   | - Tag OCR Vision    |   | /api/polly/speak |   |
|   | - deliberate_repair |   +---------------------+   +------------------+   |
|   +---------------------+                                                    |
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

## 3. The 12 MCP Tools

All 12 tools are registered on the FastMCP Streamable HTTP server and exposed via the official 2025-11-25 protocol:

| # | Tool Name | Key Parameters | Function & Output |
|---|---|---|---|
| 1 | `hear_sound` | `audio_clip_b64`, `location`, `interval_s` | Ephemeral sensor intake. Ingests raw audio, extracts spectral features, strictly wipes RAM, returns features. |
| 2 | `diagnose` | `interval_s`, `peak_freq_hz`, `duration_ms` | Matches features against `beepdb`, logs incident with provenance, creates purchase/remedy proposal. |
| 3 | `diagnose_from_description` | `interval_s`, `chirps_per_burst`, `brand`, `device_hint` | **Voice-native Alexa+ path:** Matches spoken chirp cadence, frequency perception, and brand hints against `beepdb` without requiring raw audio. |
| 4 | `list_entities` | `lifecycle_filter` | Queries the Home Graph hardware registry with verified provenance tags and lifecycle states. |
| 5 | `get_home_health` | none | Computes composite 0–100 health score, healthy/aging/EOL counts, and MCP Apps card payload. |
| 6 | `propose_action` | `kind`, `title`, `entity_id` | **Strict architectural gate:** Creates structured proposal. Never mutates outside state. |
| 7 | `confirm_action` | `proposal_id`, `confirmed` | Authorization mutation gate. Executes dispatch/order only after explicit user approval. |
| 8 | `record_incident` | `entity_id`, `description`, `severity` | Appends anomaly record to the persistent SQLite Home Graph ledger. |
| 9 | `register_entity` | `brand`, `model`, `location`, `year` | Day 0 onboarding. Registers equipment specifications and seeds warranty policies. |
| 10 | `check_warranty` | `entity_id` | Inspects policy coverage dates, active/expired status, and manufacturer replacement terms. |
| 11 | `file_warranty_claim` | `entity_id`, `reason` | Assembles free manufacturer replacement claim dossier for devices that fail within warranty. |
| 12 | `deliberate_repair` | `entity_id`, `issue_description` | **AWS Builder:** Invokes Amazon Bedrock Nova Pro for thermodynamic & financial repair-vs-replace analysis. |

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
6. **Ephemeral Volatile Clearing & Non-Persistence:** Audio is never written to disk, logs, or persistent SQLite DB (verified by automated scan test `test_audio_never_persisted_to_disk_or_db`). In-memory audio buffers are cleared best-effort immediately following feature extraction using `data.fill(0.0)` in volatile RAM.

---

## 5. The World-Model: Continuous Reliability & Thermodynamic Physics

GENIUS is not an LLM wrapper over smart-home APIs; it is a **continuous physical and temporal world model** of the home infrastructure:

### A. Continuous Reliability Hazard Modeling (Weibull Priors)
Rather than discrete, arbitrary state flags, every registered hardware entity continuously tracks reliability decay governed by a two-parameter Weibull reliability distribution:

$$R(t) = \exp\left(-\left(\frac{t}{\eta}\right)^\beta\right)$$

- **Instantaneous Hazard Rate:** $h(t) = \frac{\beta}{\eta} \left(\frac{t}{\eta}\right)^{\beta - 1}$
- **Cumulative Degradation Index:** $D(t) = 1.0 - R(t)$
- **Mean Time to Failure (MTTF):** $\text{MTTF} = \eta \cdot \Gamma\left(1 + \frac{1}{\beta}\right)$

| Hardware Family | Characteristic Life ($\eta$) | Shape Factor ($\beta$) | Physical Degradation Mechanism |
| :--- | :--- | :--- | :--- |
| **CO Detectors** | $7.0\text{ years}$ | $\beta = 3.0$ | Electrochemical sensor electrolyte dry-out & chemical exhaustion |
| **Smoke Detectors** | $10.0\text{ years}$ | $\beta = 2.5$ | Optical sensing chamber dust accumulation & photo-emitter degradation |
| **HVAC Furnaces** | $15.0\text{ years}$ | $\beta = 2.2$ | Thermal cyclic expansion, heat exchanger mechanical fatigue |
| **Water Heaters** | $10.0\text{ years}$ | $\beta = 2.0$ | Sacrificial anode depletion, galvanic tank corrosion |

Aggregate home health is mathematically derived from continuous fleet survival probability:
$$\bar{R}_{\text{fleet}} = \frac{1}{N} \sum_{i=1}^N R_i(t)$$

### B. Predictive What-If Counterfactual Simulation (Building Thermodynamics)
Before triggering proactive interventions, the Proactive Engine executes a numerical simulation of residential thermal decay using a lumped-capacitance heat transfer model:

$$\frac{dT_{\text{in}}}{dt} = -\frac{1}{\tau} (T_{\text{in}} - T_{\text{out}}) + \frac{Q_{\text{furnace}}}{C_{\text{thermal}}}$$

For unheated freeze trajectory calculations ($Q_{\text{furnace}} = 0$):
$$T_{\text{zone}}(t) = T_{\text{out}} + \big(T_{\text{zone}}(0) - T_{\text{out}}\big) \cdot e^{-t / \tau}$$

- **Branch A (Active Thermostat Maintenance):** Baseline setpoint ($68^\circ\text{F}$) maintains basement pipe envelope at $\ge 52^\circ\text{F}$. Pipe freeze probability: **$0.0\%$**.
- **Branch B (Unmitigated Furnace Lockout):** If an aging furnace trips on high filter pressure during sub-freezing ($24^\circ\text{F}$) ambient weather, the unheated pipe zone drops below $32^\circ\text{F}$ in nominal **$27.3\text{ hours}$** ($\tau_{\text{pipe}} = 16.0\text{ h}$).
- **Monte Carlo Conditioning & Probability:**
  $$P(\text{pipe zone hits } 32^\circ\text{F within } 48\text{ h} \mid \text{heat off, } 24^\circ\text{F outside, assumed } \tau_{\text{pipe}} \sim \text{Lognormal}(\ln(16), 0.3)) = \mathbf{94.1\%}$$
  *Sensitivity Note:* This probability is conditioned on the unheated cavity prior ($\tau = 16\text{ h}$). Under a less exposed cavity ($\tau = 24\text{ h}$), freeze probability drops to $66\%$; with whole-house thermal inertia ($\tau = 35\text{ h}$), it falls to $25\%$. In severe draft scenarios (10th percentile), pipe freezing occurs in as little as **$18.2\text{ hours}$**.

---

## 6. Mini-Challenges Implementation (100% Amazon Infrastructure)

### A. AWS Builder Mini-Challenge
- **Amazon Bedrock (Amazon Nova Pro `amazon.nova-pro-v1:0`):**
  - **Specialist Deliberation Panel (`deliberate_repair`):** Solves the homeowner dilemma (*"Repair or replace?"*). When an aging Carrier furnace suffers a cracked heat exchanger (\$2,200 repair quote), Nova Pro evaluates compressor age, R-410A refrigerant phaseout regulations, SEER 14 vs 18 energy efficiency differentials, and computes a 5-year TCO and payback analysis in **2.6 seconds**.
  - **Multimodal Vision Tag Ingestion (`register_entity`):** Native multimodal processing of appliance nameplate photos using Amazon Nova Pro, robustly parsing structured JSON tags with automated preamble/fence extraction.
  - **Loud Execution Tracking:** Deliberation outputs explicitly stamp `execution_mode: "live_amazon_bedrock"` and `model_used: "bedrock:amazon.nova-pro-v1:0"`.
- **Amazon Polly Neural TTS:** Real-time speech synthesis (`Joanna` neural voice) streamed directly via `/api/polly/speak` for urgent acoustic alerts and ambient maintenance guidance.

### B. Open Source Mini-Challenge (`beepdb`)
- **Published Standalone Repo:** **[github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb)**
- **License Split:** Code under MIT License; data under Creative Commons Attribution 4.0 (CC-BY 4.0).
- **Zero Copyleft Policy:** Strict rejection of Share-Alike (SA) and Non-Commercial (NC) licenses to ensure pure open-source reusability.
- **Package & CLI:** Installable via Git (`pip install git+https://github.com/patriceai-code/beepdb.git`) with CLI (`beepdb match --freq 3200 --interval 30.0` or `beepdb lookup --cadence 30 --freq 3200`).

---

## 7. Empirical Benchmark Suite & Automated Verification (19/19 Green)

To eliminate blind trust, GENIUS includes an automated empirical benchmark suite (`python benchmarks/run_benchmarks.py`) and a 19/19 pytest suite verifying spec compliance, latency budgets, and physical performance:

### Latency Budget (Deterministic End-to-End Processing)
| Stage | Execution Mechanism | Latency | Spec Constraint |
| :--- | :--- | :--- | :--- |
| **Acoustic DSP** | Hann-window FFT + Hilbert amplitude envelope | **9.80 ms** | $< 25\text{ ms}$ |
| **Ephemeral RAM Scrub** | Volatile in-memory zeroing (`data.fill(0.0)`) | **0.005 ms** | In-flight only |
| **beepdb Search** | Cadence + resonant frequency tolerance matching | **0.015 ms** | $< 1\text{ ms}$ |
| **Home Graph Ledger** | SQLite relational write with auditable provenance | **3.70 ms** | $< 10\text{ ms}$ |
| **Total Local Pipeline** | Raw PCM intake $\rightarrow$ Graph proposal staged | **13.52 ms** | **Sub-50ms real-time** |
| **Bedrock Deliberation** | Live Amazon Nova Pro 5-year TCO & payback | **~2,640 ms** | Sub-3s specialist |
| **Amazon Polly Stream** | First-chunk audio TTFB (`Joanna` neural voice) | **~180 ms** | Real-time speech |

### Classification Accuracy & Noise Robustness Gates
| Test Suite Gate | Dataset / Hardware Profile | Accuracy | Status |
| :--- | :--- | :--- | :--- |
| **Synthetic Baseline** | 20 diverse home appliances (smoke, CO, leaks, fridges, UPS) | **95.0% (19/20)\*** | PASSED |
| **Empirical Physical Piezos** | Real hardware recordings (Bloofrzo CC0 piezo transducers) | **100.0% (6/6)\*\*** | PASSED |
| **Ambient Noise Robustness** | Real domestic room noise mixed at **+15 dB SNR** | **90.0% (9/10)** | PASSED |
| **Heavy Noise Gate** | Loud kitchen domestic noise bed mixed at **+6 dB SNR** | **90.0% (9/10)** | PASSED |

*\*Note on Synthetic Mismatch: The single synthetic mismatch (clip 04) occurred because Kidde i9010 smoke detector low-battery (30s cadence, 3,100 Hz) falls within 100 Hz of Kidde CO end-of-life (30s cadence, 3,200 Hz). The matcher conservatively classifies this at the higher critical severity level.*  
*\*\*Note on Physical Piezos: Physical piezo clips were used to calibrate our initial ±350 Hz tolerance band, so this represents verification of physical component resonance rather than a held-out test split.*

```powershell
# Run the complete test suite
pytest -v tests/

# Run the automated benchmark & latency suite
python benchmarks/run_benchmarks.py
```

```
tests/test_audio_persistence.py::test_audio_never_persisted_to_disk_or_db PASSED [  5%]
tests/test_loop.py::test_state_remembers_across_loops PASSED             [ 10%]
tests/test_matcher.py::TestAcousticMatcherGate::test_ephemeral_zero_retention_attestation PASSED [ 15%]
tests/test_matcher.py::TestAcousticMatcherGate::test_acoustic_diverse_devices_gate PASSED [ 21%]
tests/test_matcher.py::TestAcousticMatcherGate::test_real_physical_recordings_gate PASSED [ 26%]
tests/test_matcher.py::TestAcousticMatcherGate::test_end_to_end_core_loop PASSED [ 31%]
tests/test_matcher.py::TestAcousticMatcherGate::test_acoustic_noise_robustness_two_levels PASSED [ 36%]
tests/test_phase1_skeleton.py::test_mcp_config PASSED                    [ 42%]
tests/test_phase1_skeleton.py::test_registered_tools PASSED              [ 47%]
tests/test_phase1_skeleton.py::test_api_tools_endpoint PASSED            [ 52%]
tests/test_phase1_skeleton.py::test_api_call_diagnose_and_confirm PASSED [ 57%]
tests/test_phase1_skeleton.py::test_mcp_streamable_http_spec_handshake PASSED [ 63%]
tests/test_phase1_skeleton.py::test_api_call_diagnose_from_description PASSED [ 68%]
tests/test_warranties_and_deliberation.py::test_device_registration_and_warranty_tracking PASSED [ 73%]
tests/test_warranties_and_deliberation.py::test_specialist_deliberation_repair_vs_replace PASSED [ 78%]
tests/test_world_model_and_reliability.py::test_weibull_continuous_reliability_calculation PASSED [ 84%]
tests/test_world_model_and_reliability.py::test_thermal_freeze_counterfactual_simulation PASSED [ 89%]
tests/test_world_model_and_reliability.py::test_parse_json_from_llm PASSED [ 94%]
tests/test_world_model_and_reliability.py::test_home_health_continuous_fleet_metrics PASSED [100%]

============================= 19 passed in 6.53s ==============================
```

- **Reference Client Compliance:** Verified against the official Model Context Protocol Python SDK's reference client (`mcp.client.streamable_http.StreamableHTTPClient`).
- **Acoustic Gates:** Empirical physical recordings (Kidde CC0, First Alert CC0, POST beeps) and synthetic regression suites tested green.
- **Physical Reliability:** Continuous Weibull distributions verified for monotonic hazard growth and exact analytic characteristic lifespan solutions.

---

## 8. Validation Limits & Honest Engineering Accounting

In the spirit of scientific integrity and hackathon transparency, we explicitly document the boundaries, assumptions, and validation limits of the current GENIUS prototype:

1. **Alexa+ Voice Interface vs Companion Sensor Intake:**  
   The current Alexa+ Preview architecture does **not** stream raw ambient room PCM audio into MCP tools. Instead, Alexa+ parses user speech into structured conversational parameters. We designed a dual-intake architecture:
   - **Voice-Native Path (`diagnose_from_description`):** The primary Alexa+ interaction model. Alexa prompts the user conversationally (*"How many seconds between beeps? Is it a single beep or a burst?"*) and passes arguments directly to `beepdb`.
   - **Acoustic Sensor Path (`hear_sound`):** An edge sensor intake (e.g. mobile companion app, auxiliary ESP32 far-field mic, or uploaded clip) where raw audio is ephemerally processed via Hilbert/FFT and strictly wiped from RAM.
2. **Synthetic Corpus vs. Physical Reality:**  
   The 20-device synthetic corpus validates that our DSP pipeline correctly extracts pulse duration, cadence, and peak frequency from synthesized audio signals. It proves mathematical correctness of the feature extraction code, but does not prove that all production smoke detectors emit idealized square waves. In fact, clip 04 (Kidde i9010 smoke detector at 3,100 Hz) was classified as Kidde CO detector (3,200 Hz) because both share a 30s cadence and fall within the ±350 Hz tolerance band, illustrating inherent acoustic overlap.
3. **Physical Piezo Calibration Scope:**  
   Our 100% (6/6) physical recording evaluation was conducted on physical piezo recordings from which our ±350 Hz empirical tolerance window was calibrated. It validates that physical piezo resonance drift is accommodated by our tolerance schema, but does not constitute an uncalibrated held-out machine learning test split.
4. **Appliance Signaling Mechanisms:**  
   While smoke and CO alarms communicate exclusively via acoustic piezoceramic buzzers, modern central HVAC furnaces (such as the Carrier Infinity 98) communicate error codes via 3-digit blinking LED boards rather than audible chirps. In GENIUS, the HVAC furnace acoustic signature is included as an illustrative proxy for complex appliance telemetry.
5. **Simulated State Boundaries:**  
   Delivery push events and Amazon order IDs (`AMZN-2026-94819`) are staged using simulated state dispatchers (`/simulate/delivery` and `/simulate/freeze`) to demonstrate end-to-end multi-day asynchronous lifecycles within a 90-second evaluation window. Production fulfillment is architecturally gated behind `confirm_action`.

---

## 9. Viable Business Model & Market Viability

GENIUS transforms Alexa from a passive voice utility into an essential home infrastructure custodian with four high-margin revenue streams:

1. **High-Intent Prime Consumables & Hardware Fulfillment:**
   When an end-of-life chirp or low battery occurs, GENIUS stages a 1-click verified replacement order directly to Amazon Prime (e.g. Kidde KN-COPP-3 \$34.99 replacement unit or Energizer 9V 4-pack \$8.99). Amazon captures immediate retail GMV and affiliate margin on high-urgency, non-price-sensitive purchases.
2. **Insurance Carrier Telemetry & Loss-Mitigation Partnerships:**
   Water leak and pipe freeze claims account for over **\$15 billion** annually in US property insurance payouts, with the average water damage claim reaching **\$12,514** *(Source: Insurance Information Institute / ISO Homeowners Claim Studies)*, and freeze pipe bursts exceeding **\$15,000–\$20,000** *(Source: State Farm Winter Claims Data)*. By mitigating freeze risks and unaddressed leaks through predictive thermodynamics, Amazon can partner with carriers (State Farm, Nationwide, Aviva) to subsidize Alexa+ subscriptions for policyholders.
3. **The Killer Differentiator for Alexa+ Subscriptions:**
   Subscribers do not pay \$9.99/month for conversational timers; they pay for proactive protection that prevents catastrophic five-figure flood disasters and explains 3 AM panic beeps with epistemic certainty.
4. **Automated Manufacturer Warranty Claim Recovery:**
   Homeowners pay **\$89–\$150** in basic service dispatch fees *(Source: Angi / HomeAdvisor 2024 Trade Survey)* often to replace a warranty-covered part. GENIUS automatically files structured warranty claim dossiers for failed in-warranty equipment, recovering \$300–\$1,500 in replacement costs for homeowners while establishing an auditable appliance provenance registry.

---

## 10. Cloud Deployment & Quickstart

### Option 1: Live AWS Cloud Web Simulator (Hosted on AWS S3)
Judges and developers can interact directly with the live AWS-hosted simulator:  
👉 **[http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com](http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com)**

*(Deployed natively onto Amazon Web Services S3 static website infrastructure with full waveform animations, empirical audio playback from S3, interactive evidence cards, and dynamic backend endpoint switching via the ⚙️ Server URL button).*

### Option 2: 1-Command AWS S3 Deployment
Deploy your own instance of the simulator to your AWS account in seconds:
```powershell
python deploy/deploy_s3_website.py
```

### Option 3: 1-Command Docker Deployment
```bash
# Clone the repository
git clone https://github.com/patriceai-code/genius.git
cd genius

# Build and start container
docker compose up --build
```
The MCP server is now live at `http://localhost:8000/mcp` and the simulator at `http://localhost:8000/client/index.html`.

### Option 4: AWS App Runner Cloud Deployment
Deploy to AWS using our CloudFormation template:
```bash
aws cloudformation create-stack \
  --stack-name genius-mcp-stack \
  --template-body file://deploy/aws-apprunner.yaml \
  --parameters ParameterKey=ImageIdentifier,ParameterValue=<YOUR_ECR_URI>:latest \
  --capabilities CAPABILITY_NAMED_IAM
```

### Option 5: Local Python Environment

**Windows (PowerShell):**
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

**macOS / Linux (Bash/Zsh):**
```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure AWS credentials (.env)
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"

# 3. Launch Uvicorn Server
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 11. Architectural Decision Records (ADRs)

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

## 12. Alignment with Official Judging Criteria

| Judging Criterion | How GENIUS Fulfills Evaluation Criteria | Empirical Proof / Receipt |
| :--- | :--- | :--- |
| **1. Tech Implementation**<br>*(Execution & Tech Leverage)* | • **Alexa+ Track:** 100% compliant self-hosted FastMCP Server speaking **MCP Streamable HTTP (2025-11-25)**, validated with the official MCP Python SDK `StreamableHTTPClient` reference client.<br>• **12 Strictly Typed Tools:** Includes voice-native `diagnose_from_description` as well as companion mic `hear_sound`.<br>• **AWS Builder Mini-Challenge:** 100% Amazon infrastructure using **Amazon Bedrock Nova Pro** (`amazon.nova-pro-v1:0`) for 5-yr TCO deliberation & tag vision, **Amazon Polly Neural TTS** (`Joanna`), and **AWS S3 Static Website Hosting**.<br>• **Open Source Mini-Challenge:** Standalone package [`beepdb`](https://github.com/patriceai-code/beepdb) with CLI, MIT code, and CC-BY 4.0 data.<br>• **Sub-15ms DSP & Zero Storage:** Hilbert transform analytic envelope $A(t)$ and volatile memory scrubbing proving zero bytes stored to disk. | • **19/19 Passing Tests** in 6.64s on Python 3.11/3.12 CI.<br>• **Total Local Pipeline Latency:** **13.52 ms**.<br>• **100% Physical Accuracy** on Bloofrzo CC0 piezo hardware.<br>• Live Bedrock Nova Pro latency: **2,640 ms**.<br>• Polly Neural TTS TTFB: **180 ms**. |
| **2. Design**<br>*(Coherence & Platform Fit)* | • **Voice-First Multimodal Synergy:** Designed specifically for Echo & Alexa+ preview devices. Natural voice handles the immediate acoustic query, while the visual surface (tablet simulator / Echo Show) renders rich **Acoustic Evidence Cards** with manual citations without verbal clutter.<br>• **The House Speaks First:** Proactive Server-Sent Events (SSE) push unprompted amber notification cards when a replacement part arrives.<br>• **Strict Propose $\rightarrow$ Confirm Trust Boundary:** Protects customer peace-of-mind by never executing transactions without explicit confirmation.<br>• **Privacy Surface:** *"What Does GENIUS Know?"* provides transparent provenance inspection and consent toggles. | • **Live Cloud Simulator:** Hosted on AWS S3 with interactive demo controls and 28 CC0 audio test clips.<br>• **ADR 001, 002, 003** documenting clean architectural patterns. |
| **3. Potential Impact**<br>*(Customer Need & Viability)* | • **Ubiquitous Need:** Solves the 3:14 AM chirping crisis across residential homes containing unmonitored piezoceramic transducers.<br>• **Massive Loss Prevention:** Prevents **$12,500** average water flood claims and **$15,000+** frozen pipe bursts via continuous building thermodynamics.<br>• **Life Safety:** Eliminates confusion where homeowners mistake expired CO alarms for low batteries.<br>• **Viable Beyond Hackathon:** 4 sustainable revenue engines: Prime fulfillment GMV (45%), carrier loss-mitigation telemetry (30%), Alexa+ \$9.99/mo retention (15%), and warranty claim recovery (10%). | • **Lumped-Capacitance Math:** Predicts pipe zone freezing in $27.3\text{ hours}$ at $24^\circ\text{F}$ ($\tau_{\text{pipe}} = 16.0\text{h}$); 5,000-run Monte Carlo yields **94.1% freeze risk**.<br>• Fully articulated business model with unit economics. |
| **4. Quality of the Idea**<br>*(Creativity & Ecosystem Mastery)* | • **From Chatbot to World-Model:** Transcends naive LLM wrappers by giving the home a continuous physical mental model that Alexa **wears**.<br>• **Mathematical Rigor:** Continuous two-parameter Weibull reliability distributions ($R(t) = \exp(-(t/\eta)^\beta)$) and dynamic fleet scores ($\bar{R}_{\text{fleet}}$).<br>• **Acoustic Privacy by Construction:** Overcomes smart home audio surveillance anxiety by actively clearing buffers immediately after FFT feature extraction and verifying zero disk retention.<br>• **Deep MCP Ecosystem Mastery:** Pioneers spec-compliant proactive push patterns over Streamable HTTP and structured proposal workflows. | • [github.com/patriceai-code/genius](https://github.com/patriceai-code/genius)<br>• [github.com/patriceai-code/beepdb](https://github.com/patriceai-code/beepdb)<br>• 12 registered MCP tools conforming to spec 2025-11-25. |

---

## 13. Attributions & Licensing

- **Code:** Licensed under the [MIT License](LICENSE).
- **Data (`beepdb`):** Licensed under [Creative Commons Attribution 4.0 International (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Audio Corpus:** Strictly limited to **CC0 (Public Domain)** and **CC-BY 4.0** audio assets. All Non-Commercial (NC) and Share-Alike (SA) licenses are rejected to guarantee license purity. Sourced catalog documented in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).

---

<div align="center">
  <sub>Built for the Amazon Developer Hackathon 2026 · Spec 2025-11-25 Streamable HTTP Transport</sub>
</div>
