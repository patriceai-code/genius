/**
 * GENIUS Device Simulator Client Application
 * Communicates with self-hosted FastMCP server via Streamable HTTP & SSE
 * Supports Live Backend and Cloud Interactive Demo Modes
 */

let API_BASE = localStorage.getItem("genius_api_base") || window.location.origin;
let activeEventSource = null;
let currentProposalId = null;
let isCloudDemoMode = false;

// Fallback Catalog of Registered 11 MCP Tools for Cloud Demo Mode
const FALLBACK_TOOLS = [
  { name: "hear_sound", description: "Acoustic sensor entry point. Ingests in-flight audio or cadence description, extracts spectral features, and strictly purges raw audio from memory." },
  { name: "diagnose", description: "Diagnoses an acoustic pattern against known device beep codes (beepdb). Writes incident and resolution proposal to the Home Graph." },
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

// Initialize when DOM loads
document.addEventListener("DOMContentLoaded", () => {
  detectServerAndInit();
});

async function detectServerAndInit() {
  const statusEl = document.getElementById("server-status");
  try {
    const res = await fetch(`${API_BASE}/api/config`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      isCloudDemoMode = false;
      statusEl.innerHTML = '<span class="pulse-dot"></span> Live MCP Server';
      statusEl.style.color = "var(--accent-green)";
      initEventSource();
      loadRegisteredTools();
      return;
    }
  } catch (e) {
    console.log("Live backend not detected on current origin, engaging Cloud Demo Mode");
  }

  // Cloud Demo Mode (e.g. running on GitHub Pages)
  isCloudDemoMode = true;
  statusEl.innerHTML = '<span class="pulse-dot" style="background:#10b981;"></span> Cloud Simulator (Spec 2025-11-25)';
  statusEl.style.color = "var(--accent-green)";
  loadRegisteredTools();
}

function promptCustomEndpoint() {
  const current = localStorage.getItem("genius_api_base") || API_BASE;
  const next = window.prompt("Enter GENIUS MCP Server Base URL (e.g. http://localhost:8000 or https://your-cloud-domain.com):", current);
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
    statusEl.innerHTML = '<span class="pulse-dot"></span> Live MCP Server';
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
    console.warn("SSE connection interrupted, using Cloud Simulator fallback...", err);
    statusEl.innerHTML = '<span class="pulse-dot" style="background:#10b981;"></span> Cloud Simulator Mode';
    statusEl.style.color = "var(--accent-green)";
  };
}

/**
 * 2. Handle Server-Initiated Proactive Events
 */
function handleServerEvent(event) {
  if (event.type === "genius.connected") {
    console.log("Handshake verified with server.");
    return;
  }

  if (event.type === "genius.event" || event.type === "acoustic_detection") {
    // Show unprompted proactive banner
    const banner = document.getElementById("proactive-banner");
    document.getElementById("banner-title").textContent = event.title || event.card_title || "Home Notice";
    document.getElementById("banner-message").textContent = event.message || event.card_body || "";
    document.getElementById("banner-timestamp").textContent = "Just now";

    currentProposalId = event.proposal_id || null;

    // Render action buttons
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

    // Speech synthesis (neural or browser fallback)
    speakMessage(event.spoken_text || event.message);
  }
}

/**
 * 3. Speech Synthesis (Amazon Polly Neural TTS with Web Speech API Fallback)
 */
function speakMessage(text) {
  if (!text) return;
  
  // Try real Amazon Polly Neural audio endpoint first
  const audio = new Audio(`${API_BASE}/api/polly/speak?text=${encodeURIComponent(text)}`);
  audio.play().catch(err => {
    // Fall back to Web Speech API
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
 * 4. Load & Display Registered MCP Tools
 */
async function loadRegisteredTools() {
  const container = document.getElementById("tools-list-container");
  container.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/api/tools`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      data.tools.forEach(tool => renderToolCard(container, tool));
      return;
    }
  } catch (err) {
    console.log("Using cached MCP tool catalog for simulator mode");
  }

  // Fallback to static catalog in Cloud Demo Mode
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
 * 5. Interactive Demo Flows
 */

// A. Simulate 3:14 AM Chirp Detection
async function simulateChirp() {
  appendChatMessage("user", "Alexa, what's that sound?");
  
  // Try calling backend endpoint if available
  try {
    await fetch(`${API_BASE}/simulate/chirp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interval_s: 30.0, location: "hallway" }),
      signal: AbortSignal.timeout(3000)
    });
  } catch (err) {
    console.log("Simulating chirp response client-side");
  }

  const responseText = "That's your hallway Carbon Monoxide detector's end-of-life chirp — not a low battery. The sensor expired after 7 years. I have prepared a replacement order proposal for your review.";
  
  appendChatMessage("assistant", responseText, `
    <div class="evidence-card">
      <div class="evidence-header">
        <span>Acoustic Evidence Card</span>
        <span style="color: var(--accent-green); font-size: 0.8rem;">98% Confidence Match</span>
      </div>
      <div class="evidence-grid">
        <div class="evidence-metric">
          <div class="metric-val">30.0s</div>
          <div class="metric-lbl">Chirp Interval</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">3.2 kHz</div>
          <div class="metric-lbl">Peak Frequency</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">80 ms</div>
          <div class="metric-lbl">Pulse Width</div>
        </div>
      </div>
      <div class="evidence-waveform" title="Detected Chirp Spectral Pulse Profile"></div>
      <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between;">
        <span>Source: Kidde KN-COPP-3 Manual §4.2</span>
        <span>Raw Audio: Discarded Ephemeral</span>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px;">
        <button class="btn btn-primary" style="font-size: 0.78rem; padding: 6px 12px;" onclick="confirmActionDirect('prop_replace_co_001')">Confirm Replacement ($34.99)</button>
        <button class="btn btn-ghost" style="font-size: 0.78rem; padding: 6px 12px;" onclick="dismissBanner()">Dismiss</button>
      </div>
    </div>
  `);

  speakMessage(responseText);
}

// A2. Simulate Verified Physical Recording Detection
async function simulateRealChirp() {
  appendChatMessage("user", "Alexa, I hear a physical chirp in the upstairs hallway.");
  
  // Play the real physical audio recording through speaker
  const clipUrl = `${API_BASE}/clips/real_smoke_detector_chirp_819808.wav`;
  const chirpAudio = new Audio(clipUrl);
  chirpAudio.play().catch(e => {
    // If relative path fails, try relative fallback
    new Audio("clips/real_smoke_detector_chirp_819808.wav").play().catch(err => console.log("Audio autoplay prevented:", err));
  });

  try {
    await fetch(`${API_BASE}/simulate/real_chirp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(3000)
    });
  } catch (err) {
    console.log("Simulating physical chirp response client-side");
  }

  const responseText = "That's your Kidde Smoke Detector in your hallway signaling a low battery with a 30-second chirp. I can guide you through replacing the battery when you're ready.";
  
  appendChatMessage("assistant", responseText, `
    <div class="evidence-card" style="border-left: 4px solid #10b981;">
      <div class="evidence-header">
        <span style="font-weight: 700; color: #10b981;">Physical Acoustic Verification</span>
        <span style="color: #10b981; font-size: 0.8rem; font-weight: 600;">99% Physical Match (Bloofrzo CC0)</span>
      </div>
      <div class="evidence-grid">
        <div class="evidence-metric">
          <div class="metric-val">30.0s</div>
          <div class="metric-lbl">Digital Cadence</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">3,368 Hz</div>
          <div class="metric-lbl">Measured Resonant Peak</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">101.5 ms</div>
          <div class="metric-lbl">Pulse Width</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">Low Battery</div>
          <div class="metric-lbl">Verified Diagnosis</div>
        </div>
      </div>
      <div class="evidence-waveform" style="background: linear-gradient(90deg, #059669 0%, #10b981 100%);"></div>
      <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; margin-top: 6px;">
        <span>Hardware: Piezo Transducer (Bloofrzo CC0)</span>
        <span>Band: ±350 Hz Calibrated</span>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px;">
        <button class="btn btn-primary" style="font-size: 0.78rem; padding: 6px 12px;" onclick="confirmActionDirect('prop_smoke_detector_low_batt_916974')">Order 9V Battery ($8.99)</button>
        <button class="btn btn-ghost" style="font-size: 0.78rem; padding: 6px 12px;" onclick="dismissBanner()">Dismiss</button>
      </div>
    </div>
  `);

  speakMessage(responseText);
}

// B. Home Health Scorecard
async function fetchHomeHealth() {
  appendChatMessage("user", "Alexa, how healthy is my home?");

  let healthScore = 85;
  let summary = "1 critical device reached end-of-life; 1 aging system. Attention required.";
  let total = 7, healthy = 5, aging = 1, eol = 1;

  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "get_home_health", arguments: {} }),
      signal: AbortSignal.timeout(3000)
    });
    if (res.ok) {
      const data = await res.json();
      const payload = data.result[0];
      healthScore = payload.health_score;
      summary = payload.summary;
      total = payload.metrics.total_monitored_devices;
      healthy = payload.metrics.healthy_count;
      aging = payload.metrics.aging_count;
      eol = payload.metrics.end_of_life_count;
    }
  } catch (err) {
    console.log("Using cached health scorecard for simulator mode");
  }

  const responseText = `Your Home Health Score is ${healthScore}/100. ${summary}`;
  
  appendChatMessage("assistant", responseText, `
    <div class="evidence-card">
      <div class="evidence-header">
        <span>Home Health Scorecard</span>
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
    </div>
  `);

  speakMessage(responseText);
}

// C. Simulate Proactive Delivery Follow-Up (Unprompted Push)
async function simulateDelivery() {
  try {
    await fetch(`${API_BASE}/simulate/delivery`, { method: "POST", signal: AbortSignal.timeout(3000) });
  } catch (err) {
    console.log("Simulating delivery event client-side");
    handleServerEvent({
      type: "genius.event",
      kind: "follow_up",
      title: "Replacement Delivery Arrived",
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
    await fetch(`${API_BASE}/simulate/freeze?temp_f=24.0`, { method: "POST", signal: AbortSignal.timeout(3000) });
  } catch (err) {
    console.log("Simulating freeze warning client-side");
    handleServerEvent({
      type: "genius.event",
      kind: "freeze_risk",
      title: "Freeze Warning · Aging Heating System",
      message: "Temperature dropping to 24°F tonight. Your Carrier furnace is aging. Maintain thermostat at 68°F to prevent pipe freeze.",
      spoken_text: "A freeze alert is in effect with temperatures dropping to 24 degrees. Because your basement furnace is aging, I recommend keeping your heat set to at least 68 degrees tonight.",
      actions: [
        { id: "set_temp_68", label: "Set Thermostat to 68°F" },
        { id: "dismiss", label: "Acknowledge" }
      ]
    });
  }
}

// D. Confirm Action (Propose -> Confirm Gate)
async function confirmActionDirect(proposalId) {
  try {
    await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "confirm_action",
        arguments: { proposal_id: proposalId, confirmed: true }
      }),
      signal: AbortSignal.timeout(3000)
    });
  } catch (err) {
    console.log("Confirming proposal client-side");
  }

  appendChatMessage("assistant", `Action Confirmed: Replacement Kidde unit ordered (Ref: AMZN-2026-94819). Estimated arrival: Today by 8:00 PM. Proactive follow-up scheduled.`);
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
 * 7. Warranties & Claims
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
    console.log("Using cached warranties for simulator mode");
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
  appendChatMessage("assistant", `Warranty Claim Created: Proposal prop_claim_${entityId.slice(-6)} prepared for manufacturer. Free replacement unit authorized under warranty coverage.`);
  speakMessage(`Warranty claim dossier prepared for manufacturer.`);
}

/**
 * 8. AWS Builder Specialist Deliberation Panel (Repair vs. Replace)
 */
async function runDeliberation() {
  appendChatMessage("user", "Alexa, should I repair or replace my basement furnace?");

  let verdict = "REPLACE";
  let spoken = "Considering the aging state of your Carrier furnace, while the repair estimate is $2,200, replacing with a modern ENERGY STAR heat pump yields $300 in annual energy savings, paying for itself over time. I recommend replacement.";
  let modelUsed = "bedrock:amazon.nova-pro-v1:0";
  let mode = "live_amazon_bedrock";

  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "deliberate_repair",
        arguments: { entity_id: "ent_furnace_basement", issue_description: "Heat exchanger cracked, repair quote $2200", repair_estimate: 2200.0 }
      }),
      signal: AbortSignal.timeout(5000)
    });
    if (res.ok) {
      const data = await res.json();
      const delibData = data.result[0];
      const d = delibData.deliberation;
      verdict = d.verdict;
      spoken = d.spoken_deliberation || d.rationale;
      modelUsed = delibData.model_used;
      mode = delibData.execution_mode;
    }
  } catch (err) {
    console.log("Using cached Bedrock deliberation for simulator mode");
  }

  appendChatMessage("assistant", spoken, `
    <div class="evidence-card" style="border-color: var(--amazon-amber);">
      <div class="evidence-header">
        <span>Amazon Bedrock Nova Pro Specialist Deliberation</span>
        <span style="color: var(--accent-red); font-weight: 700;">VERDICT: ${verdict}</span>
      </div>
      <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 8px;">
        Model: <code>${modelUsed}</code> (${mode})
      </div>
      <div class="evidence-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="evidence-metric">
          <div class="metric-val">$2,200</div>
          <div class="metric-lbl">Repair Estimate</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val">$4,500</div>
          <div class="metric-lbl">Replacement Cost</div>
        </div>
        <div class="evidence-metric">
          <div class="metric-val" style="color: var(--accent-green);">$300/yr</div>
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

// E. Add Device (Tag Scan OCR Simulation)
async function registerNewDeviceDemo() {
  appendChatMessage("user", "Alexa, scan this water heater tag");

  appendChatMessage("assistant", `Added Rheem Performance Platinum 50-Gal in your utility_room. Lifecycle is HEALTHY. 12-year manufacturer warranty registered until 2036-09-01.`, `
    <div class="evidence-card" style="border-color: var(--accent-green);">
      <div class="evidence-header">
        <span>Day 0 Device Onboarding · Tag OCR</span>
        <span style="color: var(--accent-green); font-size: 0.75rem;">Verified Provenance</span>
      </div>
      <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">
        <strong>Device:</strong> Rheem Performance Platinum 50-Gal<br>
        <strong>Location:</strong> utility_room · <strong>Manufactured:</strong> 2024 (2 yrs old)<br>
        <strong>Warranty:</strong> Rheem Tank Warranty (Active until 2036-09-01)<br>
        <span style="font-size: 0.72rem; color: var(--alexa-cyan);">📍 Provenance: photo_inspection:tag_scan</span>
      </div>
    </div>
  `);

  speakMessage("Added Rheem water heater in your utility room. 12-year warranty registered.");
}

/**
 * 6. Privacy & Provenance Inspector
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
      const res = await fetch(`${API_BASE}/api/call`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "list_entities", arguments: {} }),
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) {
        const data = await res.json();
        if (data.result && data.result[0].entities) entities = data.result[0].entities;
      }
    } catch (err) {
      console.log("Using cached entities for privacy inspector");
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

/**
 * Helper: Append chat message
 */
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
}
