/**
 * GENIUS Device Simulator Client Application
 * Spec-Compliant Model Context Protocol (MCP 2025-11-25) Streamable HTTP Client
 * Executes JSON-RPC 2.0 (initialize -> notifications/initialized -> tools/list -> tools/call)
 * directly against POST /mcp with Mcp-Session-Id header management, plus /events SSE push.
 * Includes transparent Offline Replay Mode when opened statically without a live backend.
 */

let API_BASE = localStorage.getItem("genius_api_base") || window.location.origin;
let activeEventSource = null;
let currentProposalId = null;
let isOfflineReplayMode = false;
let mcpSessionId = null;
let jsonRpcIdCounter = 1;

// Fallback Catalog of Registered 12 MCP Tools for Offline Replay Mode
const FALLBACK_TOOLS = [
  { name: "hear_sound", description: "Acoustic sensor entry point. Ingests in-flight audio or cadence description, extracts spectral features, and strictly purges raw audio from memory." },
  { name: "diagnose", description: "Diagnoses an acoustic pattern against known device beep codes (beepdb). Writes incident and resolution proposal to the Home Graph." },
  { name: "diagnose_from_description", description: "Voice-native conversational entry point for Alexa+. Matches spoken chirp cadence, frequency perception, and brand hints against beepdb without requiring raw audio." },
  { name: "list_entities", description: "Retrieves registered home devices, detectors, and infrastructure equipment from the Home Graph with verified provenance." },
  { name: "get_home_health", description: "Generates an aggregate Home Health scorecard and visual MCP Apps card payload." },
  { name: "propose_action", description: "Creates an action proposal in the Home Graph. Architectural constraint: strictly non-executing." },
  { name: "confirm_action", description: "Executes a previously proposed action after explicit user authorization (e.g. dispatch replacement purchase)." },
  { name: "record_incident", description: "Records an infrastructure anomaly, maintenance event, or acoustic observation with auditable data provenance." },
  { name: "register_entity", description: "Day 0 hardware onboarding. Ingests appliance specifications or extracts model metadata from equipment photos." },
  { name: "check_warranty", description: "Inspects active manufacturer warranty coverage, policy expiration dates, and claim eligibility." },
  { name: "file_warranty_claim", description: "Prepares a manufacturer warranty claim dossier for an in-warranty failed appliance or sensor." },
  { name: "deliberate_repair", description: "AWS Builder Specialist Deliberation. Invokes Amazon Bedrock (Nova Pro) for thermodynamic and economic repair-vs-replace analysis." }
];

document.addEventListener("DOMContentLoaded", () => {
  initMcpStreamableClient();
});

/**
 * Parses an MCP Streamable HTTP response body (supports both SSE-framed `data: {...}` and plain JSON).
 */
function parseMcpResponseBody(rawText) {
  if (!rawText) return null;
  const trimmed = rawText.trim();
  if (trimmed.startsWith("{")) {
    try {
      return JSON.parse(trimmed);
    } catch (e) {
      // fall through to line parser
    }
  }
  const lines = trimmed.split(/\r?\n/);
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (line.startsWith("data:")) {
      const payloadStr = line.slice(5).trim();
      if (payloadStr) {
        try {
          return JSON.parse(payloadStr);
        } catch (e) {
          console.warn("Failed to parse SSE JSON-RPC data line:", e);
        }
      }
    }
  }
  return null;
}

/**
 * Performs the official MCP 2025-11-25 Streamable HTTP handshake against POST /mcp:
 * 1. POST /mcp (method: "initialize") -> captures Mcp-Session-Id header
 * 2. POST /mcp (method: "notifications/initialized") with Mcp-Session-Id
 * 3. POST /mcp (method: "tools/list") to populate the tool drawer from the live MCP server
 */
async function initMcpStreamableClient() {
  const statusEl = document.getElementById("server-status");
  try {
    const initRes = await fetch(`${API_BASE}/mcp`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: jsonRpcIdCounter++,
        method: "initialize",
        params: {
          protocolVersion: "2025-11-25",
          capabilities: {},
          clientInfo: { name: "genius-alexa-plus-simulator", version: "1.0.0" }
        }
      }),
      signal: AbortSignal.timeout(2500)
    });

    if (initRes.ok) {
      mcpSessionId = initRes.headers.get("mcp-session-id") || initRes.headers.get("Mcp-Session-Id");
      isOfflineReplayMode = false;

      // Complete MCP handshake with notifications/initialized
      const notifHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
      };
      if (mcpSessionId) {
        notifHeaders["mcp-session-id"] = mcpSessionId;
      }
      await fetch(`${API_BASE}/mcp`, {
        method: "POST",
        headers: notifHeaders,
        body: JSON.stringify({
          jsonrpc: "2.0",
          method: "notifications/initialized"
        }),
        signal: AbortSignal.timeout(2000)
      });

      const shortSid = mcpSessionId ? mcpSessionId.slice(0, 8) : "active";
      statusEl.innerHTML = `<span class="pulse-dot"></span> Live MCP Session (${shortSid}…)`;
      statusEl.style.color = "var(--accent-green)";
      initEventSource();
      await loadRegisteredToolsViaMcp();
      return;
    }
  } catch (e) {
    console.log("Live MCP server not reachable on current origin; switching to Offline Replay Mode:", e);
  }

  // Transparent Offline Replay Mode (e.g. when viewing static S3 build without a local server)
  isOfflineReplayMode = true;
  mcpSessionId = null;
  statusEl.innerHTML = '<span class="pulse-dot" style="background:var(--amazon-amber);box-shadow:0 0 8px var(--amazon-amber);"></span> Offline Replay (No MCP Server Connected)';
  statusEl.style.color = "var(--amazon-amber)";
  loadRegisteredToolsViaMcp();
}

/**
 * Invokes any registered tool on the MCP server over POST /mcp using JSON-RPC 2.0 `tools/call`.
 * Automatically passes `mcp-session-id` negotiated during `initialize`.
 */
async function callMcpTool(toolName, toolArgs = {}, timeoutMs = 4500) {
  if (isOfflineReplayMode) {
    throw new Error("Offline Replay Mode active (no MCP server connected)");
  }
  if (!mcpSessionId) {
    await initMcpStreamableClient();
  }
  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
  };
  if (mcpSessionId) {
    headers["mcp-session-id"] = mcpSessionId;
  }

  const res = await fetch(`${API_BASE}/mcp`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: jsonRpcIdCounter++,
      method: "tools/call",
      params: {
        name: toolName,
        arguments: toolArgs
      }
    }),
    signal: AbortSignal.timeout(timeoutMs)
  });

  if (!res.ok) {
    throw new Error(`MCP tools/call HTTP ${res.status}`);
  }

  const rawText = await res.text();
  const rpcObj = parseMcpResponseBody(rawText);
  if (!rpcObj || !rpcObj.result || !rpcObj.result.content || !rpcObj.result.content.length) {
    throw new Error("Invalid MCP tools/call JSON-RPC response");
  }
  const textContent = rpcObj.result.content[0].text;
  return JSON.parse(textContent);
}

function promptCustomEndpoint() {
  const current = localStorage.getItem("genius_api_base") || API_BASE;
  const next = window.prompt("Enter GENIUS MCP Server Base URL (e.g. http://127.0.0.1:8000):", current);
  if (next !== null && next.trim() !== "") {
    localStorage.setItem("genius_api_base", next.trim());
    API_BASE = next.trim();
    window.location.reload();
  } else if (next === "") {
    localStorage.removeItem("genius_api_base");
    API_BASE = window.location.origin;
    window.location.reload();
  }
}

/**
 * 1. Server-Sent Events (SSE) Proactive Stream
 */
function initEventSource() {
  const statusEl = document.getElementById("server-status");
  if (activeEventSource) {
    activeEventSource.close();
  }

  activeEventSource = new EventSource(`${API_BASE}/events`);

  activeEventSource.onopen = () => {
    const shortSid = mcpSessionId ? mcpSessionId.slice(0, 8) : "active";
    statusEl.innerHTML = `<span class="pulse-dot"></span> Live MCP Session (${shortSid}…)`;
    statusEl.style.color = "var(--accent-green)";
  };

  activeEventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      console.log("[SSE Event Received]", data);
      handleServerEvent(data);
    } catch (err) {
      console.error("Failed to parse SSE event:", err);
    }
  };

  activeEventSource.onerror = (err) => {
    console.warn("SSE connection interrupted:", err);
  };
}

/**
 * 2. Handle Server-Initiated Proactive Events
 */
function handleServerEvent(event) {
  if (event.type === "genius.connected") {
    return;
  }

  if (event.type === "genius.event" || event.type === "acoustic_detection") {
    const banner = document.getElementById("proactive-banner");
    document.getElementById("banner-title").textContent = event.title || event.card_title || "Home Notice";
    document.getElementById("banner-message").textContent = event.message || event.card_body || "";
    document.getElementById("banner-timestamp").textContent = "Just now";

    currentProposalId = event.proposal_id || null;

    const actionsContainer = document.getElementById("banner-actions");
    actionsContainer.innerHTML = "";
    if (event.actions && event.actions.length > 0) {
      event.actions.forEach((act, idx) => {
        const btn = document.createElement("button");
        btn.className = idx === 0 ? "btn btn-primary" : "btn btn-ghost";
        btn.textContent = act.label;
        btn.onclick = () => handleProactiveAction(act.id, act.label);
        actionsContainer.appendChild(btn);
      });
    }

    banner.classList.remove("hidden");
    speakMessage(event.spoken_text || event.message);
  }
}

/**
 * 3. Speech Synthesis (Amazon Polly Neural TTS with Web Speech API Fallback)
 */
function speakMessage(text) {
  if (!text) return;
  const audio = new Audio(`${API_BASE}/api/polly/speak?text=${encodeURIComponent(text)}`);
  audio.play().catch(() => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  });
}

/**
 * 4. Load & Display Registered MCP Tools via JSON-RPC `tools/list` on POST /mcp
 */
async function loadRegisteredToolsViaMcp() {
  const container = document.getElementById("tools-list-container");
  container.innerHTML = "";

  if (!isOfflineReplayMode && mcpSessionId) {
    try {
      const res = await fetch(`${API_BASE}/mcp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json, text/event-stream",
          "mcp-session-id": mcpSessionId
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: jsonRpcIdCounter++,
          method: "tools/list",
          params: {}
        }),
        signal: AbortSignal.timeout(2000)
      });
      if (res.ok) {
        const rawText = await res.text();
        const rpcObj = parseMcpResponseBody(rawText);
        if (rpcObj && rpcObj.result && rpcObj.result.tools) {
          rpcObj.result.tools.forEach(tool => renderToolCard(container, tool));
          return;
        }
      }
    } catch (err) {
      console.log("Falling back to static tool list:", err);
    }
  }

  FALLBACK_TOOLS.forEach(tool => renderToolCard(container, tool));
}

function renderToolCard(container, tool) {
  const card = document.createElement("div");
  card.className = "tool-card";
  card.innerHTML = `
    <div class="tool-name">${tool.name}</div>
    <div class="tool-desc">${tool.description}</div>
  `;
  container.appendChild(card);
}

/**
 * 5. Interactive Demo Flows (All wired to POST /mcp JSON-RPC 2.0 `tools/call`)
 */

// A1. Voice-Native Conversational Diagnosis (`diagnose_from_description` over POST /mcp)
async function simulateChirp() {
  appendChatMessage(
    "user",
    "Alexa, something in the hallway is beeping once every 30 seconds — a single high-pitched chirp from our Kidde alarm."
  );

  let diag = null;
  let replayBadge = "";
  try {
    diag = await callMcpTool("diagnose_from_description", {
      interval_s: 30.0,
      chirps_per_burst: 1,
      brand: "Kidde",
      location: "hallway"
    });
  } catch (err) {
    console.log("Offline replay fallback for diagnose_from_description:", err);
    replayBadge = `<span style="color:var(--amazon-amber);font-size:0.72rem;">[OFFLINE REPLAY]</span> `;
    diag = {
      matched: true,
      entity_id: "ent_co_detector_hallway",
      device_class: "co_detector",
      brand: "Kidde",
      location: "hallway",
      meaning: "end_of_life",
      severity: "critical",
      confidence: 0.99,
      source_citation: "https://www.kidde.com/home-safety/en/us/support/help-center/browse-articles/articles/what-to-do-if-your-carbon-monoxide-alarm-is-beeping/",
      spoken_summary: "Based on a chirp every 30 seconds, that's your hallway Kidde co detector indicating end of life. This means the chemical sensor has expired after its service lifetime—not a low battery. I have prepared a replacement order proposal for your review.",
      proposal: {
        proposal_id: "prop_co_detector_end_of_l_offline",
        title: "Order Replacement Unit ($34.99)",
        cost_usd: 34.99,
        status: "staged_pending_user_confirmation"
      }
    };
  }

  const confPct = Math.round((diag.confidence || 0.95) * 100);
  const propId = (diag.proposal && (diag.proposal.proposal_id || diag.proposal.id)) || "prop_replace_co_001";
  const propTitle = (diag.proposal && diag.proposal.title) || "Confirm Replacement ($34.99)";
  currentProposalId = propId;

  appendChatMessage("assistant", diag.spoken_summary, `
    <div class="evidence-card">
      <div class="evidence-header">
        <span>${replayBadge}MCP Tool: <code>diagnose_from_description</code></span>
        <span style="color: var(--accent-green); font-size: 0.8rem;">${confPct}% Confidence · ${diag.severity.toUpperCase()}</span>
      </div>
      <div class="evidence-grid">
        <div class="evidence-metric">
          <div class="metric-val">30.0s</div>
          <div class="metric-lbl">Spoken Cadence</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">${diag.brand}</div>
          <div class="metric-lbl">Matched Brand</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">${diag.meaning.replace(/_/g, " ").toUpperCase()}</div>
          <div class="metric-lbl">Failure Mode</div>
        </div>
      </div>
      <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; margin-top: 6px;">
        <span>Citation: <a href="${diag.source_citation}" target="_blank" style="color:var(--alexa-cyan);">Manufacturer Manual</a></span>
        <span>Proposal ID: <code>${propId}</code></span>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px;">
        <button class="btn btn-primary" style="font-size: 0.78rem; padding: 6px 12px;" onclick="confirmActionDirect('${propId}')">${propTitle}</button>
        <button class="btn btn-ghost" style="font-size: 0.78rem; padding: 6px 12px;" onclick="dismissBanner()">Dismiss</button>
      </div>
    </div>
  `);

  speakMessage(diag.spoken_summary);
}

// A2. Companion Sensor Physical Chirp DSP (`hear_sound` -> `diagnose` over POST /mcp)
async function simulateRealChirp() {
  appendChatMessage(
    "user",
    "Companion Sensor Intake: Analyze physical piezo recording (real_smoke_detector_chirp_819808.wav) with user-reported 30s cadence."
  );

  const clipUrl = `${API_BASE}/clips/real_smoke_detector_chirp_819808.wav`;
  new Audio(clipUrl).play().catch(() => {
    new Audio("clips/real_smoke_detector_chirp_819808.wav").play().catch(() => {});
  });

  let hsData = null;
  let diagData = null;
  let replayBadge = "";

  try {
    // 1. Call `hear_sound` over POST /mcp to extract actual Hilbert/FFT features from WAV
    hsData = await callMcpTool("hear_sound", {
      clip_path: "tests/clips/real_smoke_detector_chirp_819808.wav",
      location: "hallway"
    });
    const measuredFreq = hsData.features.peak_frequency_hz;
    const measuredDur = hsData.features.pulse_duration_ms;

    // 2. Pass the live extracted features from `hear_sound` into `diagnose` over POST /mcp
    diagData = await callMcpTool("diagnose", {
      interval_s: 30.0,
      peak_freq_hz: measuredFreq,
      duration_ms: measuredDur,
      location: "hallway",
      clip_id: hsData.clip_id
    });
  } catch (err) {
    console.log("Offline replay fallback for hear_sound + diagnose:", err);
    replayBadge = `<span style="color:var(--amazon-amber);font-size:0.72rem;">[OFFLINE REPLAY]</span> `;
    hsData = {
      clip_id: "real_smoke_detector_chirp_819808.wav",
      features: { peak_frequency_hz: 3368.1, pulse_duration_ms: 101.5, interval_s: 0.0 },
      privacy_attestation: { raw_audio_persisted: false, retention_policy: "discard_immediately_in_flight" }
    };
    diagData = {
      brand: "Kidde",
      device_class: "smoke_detector",
      meaning: "low_battery",
      confidence: 0.99,
      spoken_summary: "That's your Kidde Smoke Detector in your hallway signaling a low battery with a 30-second chirp. I can guide you through replacing the battery when you're ready.",
      proposal: { id: "prop_smoke_detector_low_batt_offline", title: "Order 9V Batteries / Walkthrough" },
      source_provenance: "manufacturer_manual:https://www.kidde.com/home-safety/en/us/support/"
    };
  }

  const freqVal = hsData.features.peak_frequency_hz.toFixed(1);
  const durVal = hsData.features.pulse_duration_ms.toFixed(1);
  const confPct = Math.round((diagData.confidence || 0.99) * 100);
  const propId = (diagData.proposal && diagData.proposal.id) || "prop_smoke_low_batt";
  const propTitle = (diagData.proposal && diagData.proposal.title) || "Order 9V Battery ($8.99)";
  currentProposalId = propId;

  appendChatMessage("assistant", diagData.spoken_summary, `
    <div class="evidence-card" style="border-left: 4px solid #10b981;">
      <div class="evidence-header">
        <span style="font-weight: 700; color: #10b981;">${replayBadge}MCP Pipeline: <code>hear_sound</code> → <code>diagnose</code></span>
        <span style="color: #10b981; font-size: 0.8rem; font-weight: 600;">${confPct}% Match (${diagData.brand} ${diagData.device_class.replace(/_/g, " ")})</span>
      </div>
      <div class="evidence-grid">
        <div class="evidence-metric">
          <div class="metric-val">30.0s</div>
          <div class="metric-lbl">User-Reported Cadence</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">${freqVal} Hz</div>
          <div class="metric-lbl">Measured FFT Peak</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">${durVal} ms</div>
          <div class="metric-lbl">Measured Hilbert Width</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">${diagData.meaning.replace(/_/g, " ")}</div>
          <div class="metric-lbl">Diagnosed State</div>
        </div>
      </div>
      <div class="evidence-waveform" style="background: linear-gradient(90deg, #059669 0%, #10b981 100%);"></div>
      <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; margin-top: 6px;">
        <span>Clip: <code>${hsData.clip_id}</code> (1.0s CC0 sample)</span>
        <span>Persisted Audio: <code>${hsData.privacy_attestation.raw_audio_persisted ? "YES" : "0 Bytes (RAM Zeroed)"}</code></span>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px;">
        <button class="btn btn-primary" style="font-size: 0.78rem; padding: 6px 12px;" onclick="confirmActionDirect('${propId}')">${propTitle}</button>
        <button class="btn btn-ghost" style="font-size: 0.78rem; padding: 6px 12px;" onclick="dismissBanner()">Dismiss</button>
      </div>
    </div>
  `);

  speakMessage(diagData.spoken_summary);
}

// B. Home Health Scorecard (`get_home_health` over POST /mcp)
async function fetchHomeHealth() {
  appendChatMessage("user", "Alexa, how healthy is my home?");

  let healthScore = 85;
  let summary = "1 critical device reached end-of-life; 1 aging system. Attention required.";
  let total = 7, healthy = 5, aging = 1, eol = 1, fleetRel = 88.5;
  let replayBadge = "";

  try {
    const payload = await callMcpTool("get_home_health", {});
    healthScore = payload.health_score;
    summary = payload.summary;
    total = payload.metrics.total_monitored_devices;
    healthy = payload.metrics.healthy_count;
    aging = payload.metrics.aging_count;
    eol = payload.metrics.end_of_life_count;
    if (payload.continuous_reliability) {
      fleetRel = payload.continuous_reliability.fleet_reliability_pct;
    }
  } catch (err) {
    console.log("Offline replay fallback for get_home_health:", err);
    replayBadge = `<span style="color:var(--amazon-amber);font-size:0.72rem;">[OFFLINE REPLAY]</span> `;
  }

  const responseText = `Your Home Health Score is ${healthScore}/100. ${summary}`;

  appendChatMessage("assistant", responseText, `
    <div class="evidence-card">
      <div class="evidence-header">
        <span>${replayBadge}MCP Tool: <code>get_home_health</code></span>
        <span style="color: var(--amazon-amber); font-weight: 700; font-size: 0.95rem;">Score: ${healthScore}/100</span>
      </div>
      <div class="evidence-grid" style="grid-template-columns: repeat(4, 1fr);">
        <div class="evidence-metric">
          <div class="metric-val">${total}</div>
          <div class="metric-lbl">Monitored</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val" style="color: var(--accent-green);">${healthy}</div>
          <div class="metric-lbl">Healthy</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val" style="color: var(--amazon-amber);">${aging}</div>
          <div class="metric-lbl">Aging</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val" style="color: var(--accent-red);">${eol}</div>
          <div class="metric-lbl">EOL</div>
        </div>
      </div>
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 10px; display: flex; justify-content: space-between; border-top: 1px solid var(--border-color); padding-top: 6px;">
        <span>Weibull Fleet Reliability: <strong style="color: var(--accent-green);">${fleetRel}%</strong></span>
        <span>Model: Continuous Hazard Decay</span>
      </div>
    </div>
  `);

  speakMessage(responseText);
}

// C. Simulate Proactive Delivery Follow-Up (Unprompted SSE Push)
async function simulateDelivery() {
  try {
    const res = await fetch(`${API_BASE}/simulate/delivery`, { method: "POST", signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error("Delivery endpoint returned non-200");
  } catch (err) {
    console.log("Offline replay fallback for delivery event");
    handleServerEvent({
      type: "genius.event",
      kind: "follow_up",
      title: "[Offline Replay] Replacement Delivery Arrived",
      message: "Your Kidde CO detector replacement arrived today. Is the hallway unit still chirping?",
      spoken_text: "Your replacement carbon monoxide alarm just arrived on your front porch. Would you like me to walk you through replacing the hallway unit?",
      actions: [
        { id: "walkthrough", label: "Walk me through replacement" },
        { id: "dismiss", label: "Dismiss" }
      ]
    });
  }
}

// C2. Simulate Proactive Freeze Alert
async function simulateFreeze() {
  try {
    const res = await fetch(`${API_BASE}/simulate/freeze?temp_f=24.0`, { method: "POST", signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error("Freeze endpoint returned non-200");
  } catch (err) {
    console.log("Offline replay fallback for freeze warning");
    handleServerEvent({
      type: "genius.event",
      kind: "freeze_risk",
      title: "[Offline Replay] Freeze Warning · Aging Heating System",
      message: "Temperature dropping to 24°F tonight. Your Carrier furnace is aging (manufactured 2015). Simulation projects pipe freeze risk within 27.3h if unmitigated. Maintain thermostat at 68°F.",
      spoken_text: "A freeze alert is in effect with temperatures dropping to 24 degrees. Because your basement furnace is aging, I recommend keeping your heat set to at least 68 degrees tonight.",
      actions: [
        { id: "set_temp_68", label: "Set Thermostat to 68°F" },
        { id: "dismiss", label: "Acknowledge" }
      ]
    });
  }
}

// D. Confirm Action (`confirm_action` over POST /mcp)
async function confirmActionDirect(proposalId) {
  let confData = null;
  let replayBadge = "";
  try {
    confData = await callMcpTool("confirm_action", {
      proposal_id: proposalId,
      confirmed: true
    });
  } catch (err) {
    console.log("Offline replay fallback for confirm_action:", err);
    replayBadge = "[OFFLINE REPLAY] ";
    confData = {
      proposal_id: proposalId,
      status: "confirmed_and_executed",
      timestamp: new Date().toISOString(),
      result: {
        order_ref: `AMZN-2026-94819-${proposalId.slice(-6).toUpperCase()}`,
        item: "Replacement Hardware Unit",
        estimated_delivery: "Today by 6:00 PM (Simulated Fulfillment)"
      },
      message: `Action confirmed for ${proposalId}.`
    };
  }

  const orderRef = (confData.result && confData.result.order_ref) || "AMZN-2026-94819";
  const itemDesc = (confData.result && confData.result.item) || "Replacement Unit";
  const eta = (confData.result && confData.result.estimated_delivery) || "Today by 6:00 PM";

  appendChatMessage(
    "assistant",
    `${replayBadge}MCP confirm_action (${confData.proposal_id}): ${itemDesc} staged (Order Ref: ${orderRef}, ETA: ${eta}). Proactive delivery follow-up armed in Home Graph.`
  );
  dismissBanner();
}

function handleProactiveAction(actionId, label) {
  if (actionId === "confirm") {
    confirmActionDirect(currentProposalId || "prop_replace_co_001");
  } else if (actionId === "walkthrough") {
    appendChatMessage("user", "Walk me through replacing the unit");
    appendChatMessage("assistant", "Step 1: Twist the old Kidde unit counter-clockwise from its mounting bracket. Step 2: Unplug the wiring harness. Step 3: Plug the harness into the new 10-year sealed unit and twist clockwise until it clicks.");
    speakMessage("Twist the old unit counter-clockwise, unplug the wiring harness, and connect your new unit.");
    dismissBanner();
  } else if (actionId === "set_temp_68") {
    appendChatMessage("user", "Set thermostat to 68°F");
    appendChatMessage("assistant", "Thermostat set to 68°F. Carrier furnace active to protect basement pipes from freeze damage.");
    speakMessage("Thermostat set to 68 degrees to protect against the freeze.");
    dismissBanner();
  } else {
    dismissBanner();
  }
}

function toggleConsent(category, isEnabled) {
  const status = isEnabled ? "enabled" : "disabled";
  appendChatMessage("assistant", `Privacy Setting Updated: ${category.toUpperCase()} has been ${status}.`);
}

function dismissBanner() {
  document.getElementById("proactive-banner").classList.add("hidden");
}

/**
 * 7. Warranties & Claims (`check_warranty` / `file_warranty_claim` over POST /mcp)
 */
async function checkWarranties() {
  appendChatMessage("user", "Alexa, what warranties do I have on my equipment?");

  const sampleWarranties = [
    { entity_id: "ent_furnace_basement", brand: "Carrier", model: "Infinity 98", location: "basement", end_date: "2025-10-15", provider: "Carrier 10-Yr Limited" },
    { entity_id: "ent_water_heater_utility", brand: "Rheem", model: "Performance Platinum", location: "utility_room", end_date: "2036-09-01", provider: "Rheem Tank Warranty" },
    { entity_id: "ent_fridge_kitchen", brand: "Samsung", model: "Family Hub RF28", location: "kitchen", end_date: "2029-05-12", provider: "Samsung Sealed System" }
  ];

  let list = sampleWarranties;
  try {
    const res = await fetch(`${API_BASE}/api/warranties`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      if (data.warranties && data.warranties.length > 0) list = data.warranties;
    }
  } catch (err) {
    console.log("Using cached warranties for offline replay mode");
  }

  let itemsHtml = "";
  list.forEach(w => {
    const isExp = new Date(w.end_date) < new Date("2026-09-26");
    const badgeColor = isExp ? "var(--accent-red)" : "var(--accent-green)";
    const badgeText = isExp ? "EXPIRED" : "ACTIVE COVERAGE";
    itemsHtml += `
      <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; margin-top: 8px;">
        <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.85rem;">
          <span>${w.brand} ${w.model} (${w.location})</span>
          <span style="color: ${badgeColor}; font-size: 0.75rem;">${badgeText}</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); margin: 4px 0;">Provider: ${w.provider} · Valid until: ${w.end_date}</div>
        ${!isExp ? `<button class="btn btn-primary" style="font-size: 0.72rem; padding: 4px 10px; margin-top: 4px;" onclick="fileWarrantyClaimDirect('${w.entity_id}')">File Free Replacement Claim</button>` : ''}
      </div>
    `;
  });

  appendChatMessage("assistant", `I found ${list.length} hardware systems tracked in your Home Graph with registered warranty policies.`, `
    <div class="evidence-card" style="border-color: var(--alexa-cyan);">
      <div class="evidence-header">
        <span>Warranty & Protection Ledger</span>
        <span style="font-size: 0.75rem; color: var(--alexa-cyan);">${list.length} Policies Active</span>
      </div>
      ${itemsHtml}
    </div>
  `);
  speakMessage(`You have ${list.length} hardware warranties logged in your home graph.`);
}

async function fileWarrantyClaimDirect(entityId) {
  try {
    const claimRes = await callMcpTool("file_warranty_claim", {
      entity_id: entityId,
      failure_description: "Failed component under active warranty policy"
    });
    appendChatMessage("assistant", `MCP file_warranty_claim: Claim ${claimRes.claim_id || entityId} staged for ${claimRes.brand || "Manufacturer"}.`);
  } catch (err) {
    appendChatMessage("assistant", `[OFFLINE REPLAY] Warranty Claim Created: Proposal prop_claim_${entityId.slice(-6)} prepared for manufacturer.`);
  }
  speakMessage("Warranty claim dossier prepared for manufacturer.");
}

/**
 * 8. AWS Builder Specialist Deliberation Panel (`deliberate_repair` over POST /mcp)
 */
async function runDeliberation() {
  appendChatMessage("user", "Alexa, should I repair or replace my basement furnace?");

  let verdict = "REPLACE";
  let spoken = "Considering the aging state of your Carrier furnace, while the repair estimate is $2,200, replacing with a modern ENERGY STAR heat pump yields $300 in annual energy savings, paying for itself over time. I recommend replacement.";
  let modelUsed = "bedrock:amazon.nova-pro-v1:0";
  let mode = "offline_replay_fallback";
  let repairCost = 2200;
  let replaceCost = 4500;
  let annualSavings = 300;

  try {
    const delibData = await callMcpTool("deliberate_repair", {
      entity_id: "ent_furnace_basement",
      issue_description: "Heat exchanger cracked, repair quote $2200",
      repair_estimate: 2200.0
    }, 8000);
    const d = delibData.deliberation;
    verdict = d.verdict;
    spoken = d.spoken_deliberation || d.rationale;
    modelUsed = delibData.model_used;
    mode = delibData.execution_mode;
    if (d.financial_analysis) {
      repairCost = d.financial_analysis.repair_estimate_usd || 2200;
      replaceCost = d.financial_analysis.replacement_estimate_usd || 4500;
      annualSavings = d.financial_analysis.estimated_annual_energy_savings_usd || 300;
    }
  } catch (err) {
    console.log("Using offline replay fallback for Bedrock deliberation:", err);
  }

  appendChatMessage("assistant", spoken, `
    <div class="evidence-card" style="border-color: var(--amazon-amber);">
      <div class="evidence-header">
        <span>MCP Tool: <code>deliberate_repair</code> (Amazon Bedrock)</span>
        <span style="color: var(--accent-red); font-weight: 700;">VERDICT: ${verdict}</span>
      </div>
      <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 8px;">
        Model: <code>${modelUsed}</code> · Mode: <code>${mode}</code>
      </div>
      <div class="evidence-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="evidence-metric">
          <div class="metric-val">$${repairCost.toLocaleString()}</div>
          <div class="metric-lbl">Repair Estimate</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">$${replaceCost.toLocaleString()}</div>
          <div class="metric-lbl">Replacement Cost</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val" style="color: var(--accent-green);">$${annualSavings}/yr</div>
          <div class="metric-lbl">SEER Savings</div>
        </div>
      </div>
      <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 8px;">
        Thermodynamic factor: Cracked heat exchanger + R-410A refrigerant phaseout makes ongoing maintenance economically disadvantageous.
      </div>
    </div>
  `);

  speakMessage(spoken);
}

// E. Add Device (`register_entity` over POST /mcp)
async function registerNewDeviceDemo() {
  appendChatMessage("user", "Alexa, scan this water heater tag");

  let regData = null;
  try {
    regData = await callMcpTool("register_entity", {
      entity_type: "water_heater",
      brand: "Rheem",
      model: "Performance Platinum 50-Gal",
      location: "utility_room",
      manufacture_year: 2024,
      warranty_years: 12
    });
  } catch (err) {
    regData = {
      brand: "Rheem",
      model: "Performance Platinum 50-Gal",
      location: "utility_room",
      manufacture_year: 2024,
      lifecycle_state: "healthy",
      warranty_end_date: "2036-09-01",
      provenance: "photo_inspection:tag_scan"
    };
  }

  appendChatMessage("assistant", `Added ${regData.brand || "Rheem"} ${regData.model || "Performance Platinum 50-Gal"} in your ${regData.location || "utility_room"}. Lifecycle is HEALTHY. 12-year manufacturer warranty registered.`, `
    <div class="evidence-card" style="border-color: var(--accent-green);">
      <div class="evidence-header">
        <span>MCP Tool: <code>register_entity</code> · Tag OCR</span>
        <span style="color: var(--accent-green); font-size: 0.75rem;">Verified Provenance</span>
      </div>
      <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">
        <strong>Device:</strong> ${regData.brand || "Rheem"} ${regData.model || "Performance Platinum 50-Gal"}<br>
        <strong>Location:</strong> ${regData.location || "utility_room"} · <strong>Manufactured:</strong> ${regData.manufacture_year || 2024}<br>
        <strong>Warranty:</strong> Rheem Tank Warranty (Active)<br>
        <span style="font-size: 0.72rem; color: var(--alexa-cyan);">📍 Provenance: ${regData.provenance || "photo_inspection:tag_scan"}</span>
      </div>
    </div>
  `);

  speakMessage("Added Rheem water heater in your utility room. 12-year warranty registered.");
}

/**
 * 6. Privacy & Provenance Inspector (`list_entities` over POST /mcp)
 */
async function openPrivacyInspector() {
  const drawer = document.getElementById("privacy-inspector");
  drawer.classList.toggle("hidden");

  if (!drawer.classList.contains("hidden")) {
    const defaultEntities = [
      { brand: "Kidde", model: "KN-COPP-3", location: "hallway", manufacture_year: 2018, lifecycle_state: "end_of_life", provenance: "manual:kidde.com/support" },
      { brand: "Kidde", model: "i9010 Smoke Alarm", location: "hallway", manufacture_year: 2021, lifecycle_state: "healthy", provenance: "acoustic_dsp:fft_3368hz" },
      { brand: "Carrier", model: "Infinity 98 Furnace", location: "basement", manufacture_year: 2015, lifecycle_state: "aging", provenance: "photo_inspection:tag_scan" },
      { brand: "Rheem", model: "Performance Platinum", location: "utility_room", manufacture_year: 2024, lifecycle_state: "healthy", provenance: "photo_inspection:tag_scan" }
    ];

    let entities = defaultEntities;
    try {
      const data = await callMcpTool("list_entities", {});
      if (data && data.entities) entities = data.entities;
    } catch (err) {
      console.log("Using cached entities for offline replay mode");
    }

    const container = document.getElementById("entities-container");
    container.innerHTML = "";

    entities.forEach(ent => {
      const item = document.createElement("div");
      item.className = "entity-item";
      item.innerHTML = `
        <div class="entity-top">
          <span>${ent.brand} ${ent.model}</span>
          <span style="color: ${ent.lifecycle_state === 'end_of_life' ? 'var(--accent-red)' : 'var(--accent-green)'}">
            ${ent.lifecycle_state.toUpperCase()}
          </span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 4px;">Location: ${ent.location} · Year: ${ent.manufacture_year}</div>
        <div class="provenance-tag">📍 Provenance: ${ent.provenance}</div>
      `;
      container.appendChild(item);
    });
  }
}

function toggleToolExplorer() {
  const drawer = document.getElementById("tool-explorer");
  drawer.classList.toggle("hidden");
}

function appendChatMessage(sender, text, extraHtml = "") {
  const thread = document.getElementById("chat-thread");
  const msg = document.createElement("div");
  msg.className = `message ${sender}-message`;

  const senderLabel = sender === "user" ? "You" : "GENIUS (World Model)";
  msg.innerHTML = `
    <div class="message-sender">${senderLabel}</div>
    <div class="message-text">${text}</div>
    ${extraHtml}
  `;

  thread.appendChild(msg);
  thread.scrollTop = thread.scrollHeight;
  const conv = document.querySelector(".conversation-container");
  if (conv) {
    conv.scrollTop = conv.scrollHeight;
  }
}
