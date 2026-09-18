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

---

## Core Loop & Principles

1. **The Core Loop:**
   $$\text{Sound} \longrightarrow \text{Diagnosis} \longrightarrow \text{Graph State} \longrightarrow \text{Proactive Event} \longrightarrow \text{Confirmed Action}$$
2. **Ephemeral by Design:** Acoustic input is processed strictly in-flight. Spectral features (chirp interval, duration, peak frequency) are extracted in volatile memory, and raw audio buffers are immediately discarded before the response returns.
3. **Propose $\rightarrow$ Confirm:** The system never executes external mutations (orders, dispatches, mode switches) autonomously. It creates structured proposals that require explicit user confirmation.

---

## Tech Stack

- **MCP Server:** Python MCP SDK, FastMCP / Starlette (Streamable HTTP transport)
- **API & SSE Server:** FastAPI / Uvicorn
- **Home Graph:** SQLite (with strict provenance auditing)
- **Acoustic Intelligence:** SciPy / NumPy / SoundFile (spectral peaks & cadence estimation)
- **Manual Knowledge Extraction:** Amazon Bedrock (Claude 3.5 Sonnet / Haiku)
- **Simulator Speech:** Amazon Polly (Neural Voice)
- **Client Frontend:** Vanilla HTML5 / ES6 / CSS3 (Zero build tooling, native `EventSource`)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Audio clips and dataset sources adhere to the CC0 / CC-BY protocol detailed in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
>>>>>>> f29d3c9 (feat(foundations): initial commit with project structure, license, attributions, and architecture records)
