/**
 * GENIUS Device Simulator Client Application
 * Communicates with self-hosted FastMCP server via Streamable HTTP & SSE
 */

const API_BASE = window.location.origin;
let activeEventSource = null;
let currentProposalId = null;

// Initialize when DOM loads
document.addEventListener("DOMContentLoaded", () => {
  initEventSource();
  loadRegisteredTools();
});

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
    statusEl.innerHTML = '<span class="pulse-dot"></span> Connected to FastMCP';
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
    console.warn("SSE connection interrupted, retrying...", err);
    statusEl.innerHTML = 'Connecting to FastMCP...';
    statusEl.style.color = "var(--amazon-amber)";
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

  if (event.type === "genius.event") {
    // Show unprompted proactive banner
    const banner = document.getElementById("proactive-banner");
    document.getElementById("banner-title").textContent = event.title || "Home Notice";
    document.getElementById("banner-message").textContent = event.message || "";
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

    // Optional voice synthesis (neural or browser fallback)
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
 * 4. Load & Display 7 Registered MCP Tools
 */
async function loadRegisteredTools() {
  try {
    const res = await fetch(`${API_BASE}/api/tools`);
    const data = await res.json();
    const container = document.getElementById("tools-list-container");
    container.innerHTML = "";

    data.tools.forEach(tool => {
      const card = document.createElement("div");
      card.className = "tool-card";
      card.innerHTML = `
        <div class="tool-name">${tool.name}</div>
        <div class="tool-desc">${tool.description}</div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load registered tools:", err);
  }
}

/**
 * 5. Interactive Demo Flows
 */

// A. Simulate 3:14 AM Chirp Detection
async function simulateChirp() {
  appendChatMessage("user", "Alexa, what's that sound?");
  
  try {
    const res = await fetch(`${API_BASE}/simulate/chirp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interval_s: 30.0, location: "hallway" })
    });
    const data = await res.json();
    
    const responseText = "That's your hallway Carbon Monoxide detector's end-of-life chirp — not a low battery. The sensor expired after 7 years. I have prepared a replacement order proposal for your review.";
    
    // Append Assistant response with Evidence Card
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
  } catch (err) {
    console.error("Chirp simulation failed:", err);
  }
}

// A2. Simulate Verified Physical Recording Detection
async function simulateRealChirp() {
  appendChatMessage("user", "Alexa, I hear a physical chirp in the upstairs hallway.");
  
  // Play the real physical audio recording through speaker
  const chirpAudio = new Audio(`${API_BASE}/clips/real_smoke_detector_chirp_819808.wav`);
  chirpAudio.play().catch(e => console.log("Audio autoplay prevented:", e));

  try {
    const res = await fetch(`${API_BASE}/simulate/real_chirp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const data = await res.json();
    
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
        <div class="action-proposal-box">
          <div class="proposal-title">Action Proposal: Order 9V Replacement Battery</div>
          <div class="proposal-desc">Strict Propose & Confirm model: Proposal created in Home Graph. Never executes without your authorization.</div>
          <div class="proposal-actions">
            <button class="btn btn-confirm" onclick="confirmActionDirect('Order 9V Battery ($8.99)')">Authorize Order ($8.99)</button>
            <button class="btn btn-dismiss" onclick="dismissActionDirect()">Dismiss</button>
          </div>
        </div>
      </div>
    `);
    
    speakMessage(responseText);
  } catch (err) {
    console.error("Real chirp simulation failed:", err);
  }
}

// B. Home Health Scorecard

async function fetchHomeHealth() {
  appendChatMessage("user", "Alexa, what's my home's health?");

  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "get_home_health", arguments: {} })
    });
    const data = await res.json();
    const health = data.result[0];

    const responseText = `Your home health score is ${health.health_score}/100. ${health.summary}`;

    appendChatMessage("assistant", responseText, `
      <div class="evidence-card" style="border-color: var(--amazon-amber);">
        <div class="evidence-header">
          <span>Home Infrastructure Scorecard</span>
          <span style="color: var(--amazon-amber); font-weight: 700;">${health.health_score} / 100</span>
        </div>
        <div class="evidence-grid">
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--accent-green);">${health.metrics.healthy_count}</div>
            <div class="metric-lbl">Healthy</div>
          </div>
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--amazon-amber);">${health.metrics.aging_count}</div>
            <div class="metric-lbl">Aging</div>
          </div>
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--accent-red);">${health.metrics.end_of_life_count}</div>
            <div class="metric-lbl">End of Life</div>
          </div>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px;">
          <strong>Active Incident:</strong> ${health.urgent_incidents[0].device} (${health.urgent_incidents[0].issue})
        </div>
      </div>
    `);

    speakMessage(responseText);
  } catch (err) {
    console.error("Failed to fetch home health:", err);
  }
}

// C. Simulate Proactive Push (Delivery Arrival)
async function simulateDelivery() {
  try {
    await fetch(`${API_BASE}/simulate/delivery`, { method: "POST" });
  } catch (err) {
    console.error("Delivery simulation failed:", err);
  }
}

// C2. Simulate Proactive Freeze Alert
async function simulateFreeze() {
  try {
    await fetch(`${API_BASE}/simulate/freeze?temp_f=24.0`, { method: "POST" });
  } catch (err) {
    console.error("Freeze alert simulation failed:", err);
  }
}

// D. Confirm Action (Propose -> Confirm Gate)
async function confirmActionDirect(proposalId) {
  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "confirm_action",
        arguments: { proposal_id: proposalId, confirmed: true }
      })
    });
    const data = await res.json();
    const result = data.result[0];
    
    appendChatMessage("assistant", `Action Confirmed: ${result.result.item} has been ordered (Ref: ${result.result.order_ref}). Estimated arrival: ${result.result.estimated_delivery}. Proactive follow-up scheduled.`);
    dismissBanner();
  } catch (err) {
    console.error("Action confirmation failed:", err);
  }
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
  try {
    const res = await fetch(`${API_BASE}/api/warranties`);
    const data = await res.json();
    const list = data.warranties;

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
  } catch (err) {
    console.error("Failed to load warranties:", err);
  }
}

async function fileWarrantyClaimDirect(entityId) {
  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "file_warranty_claim",
        arguments: { entity_id: entityId, reason: "Acoustic chirp detected; sensor failed in warranty period" }
      })
    });
    const data = await res.json();
    const result = data.result[0];

    appendChatMessage("assistant", `Warranty Claim Created: Proposal ${result.proposal.id} prepared for ${result.provider}. Free replacement unit authorized under manufacturer coverage.`);
    speakMessage(`Warranty claim dossier prepared for ${result.provider}.`);
  } catch (err) {
    console.error("Claim filing failed:", err);
  }
}

/**
 * 8. AWS Builder Specialist Deliberation Panel (Repair vs. Replace)
 */
async function runDeliberation() {
  appendChatMessage("user", "Alexa, should I repair or replace my basement furnace?");

  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "deliberate_repair",
        arguments: { entity_id: "ent_furnace_basement" }
      })
    });
    const data = await res.json();
    const delibData = data.result[0];
    const d = delibData.deliberation;
    const f = d.financial_breakdown;

    const responseText = d.spoken_deliberation || d.rationale;

    appendChatMessage("assistant", responseText, `
      <div class="evidence-card" style="border-color: var(--amazon-amber);">
        <div class="evidence-header">
          <span>Amazon Bedrock Engineering Specialist Deliberation</span>
          <span style="color: var(--accent-red); font-weight: 700;">VERDICT: ${d.verdict}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.4;">
          ${d.rationale}
        </div>
        <div class="evidence-grid" style="grid-template-columns: repeat(4, 1fr);">
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--accent-red);">$${f.estimated_repair_cost}</div>
            <div class="metric-lbl">Repair Cost</div>
          </div>
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--alexa-cyan);">$${f.replacement_equipment_cost}</div>
            <div class="metric-lbl">New Unit</div>
          </div>
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--accent-green);">$${f.annual_efficiency_savings}/yr</div>
            <div class="metric-lbl">Energy Savings</div>
          </div>
          <div class="evidence-metric">
            <div class="metric-val" style="color: var(--amazon-amber);">${f.payback_period_years} yrs</div>
            <div class="metric-lbl">Payback Period</div>
          </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between;">
          <span>Model: Claude 3.5 Sonnet on Amazon Bedrock</span>
          <span>5-Year Net Benefit: +$${f.five_year_net_difference}</span>
        </div>
      </div>
    `);

    speakMessage(responseText);
  } catch (err) {
    console.error("Deliberation failed:", err);
  }
}

/**
 * 9. Day 0 Hardware Onboarding (Tag Scan)
 */
async function registerNewDeviceDemo() {
  appendChatMessage("user", "Alexa, scan this equipment tag to add it to my home.");

  try {
    const res = await fetch(`${API_BASE}/api/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "register_entity",
        arguments: {
          entity_type: "water_heater",
          brand: "Rheem",
          model: "Performance Platinum 50-Gal",
          location: "utility_room",
          manufacture_year: 2024,
          warranty_years: 12,
          warranty_provider: "Rheem Tank Warranty"
        }
      })
    });
    const data = await res.json();
    const result = data.result[0];

    const responseText = `Added ${result.entity.brand} ${result.entity.model} in your ${result.entity.location}. Lifecycle is ${result.entity.lifecycle_state.toUpperCase()}. 12-year warranty registered until ${result.warranty.valid_until}.`;

    appendChatMessage("assistant", responseText, `
      <div class="evidence-card" style="border-color: var(--accent-green);">
        <div class="evidence-header">
          <span>Day 0 Device Onboarding · Tag OCR</span>
          <span style="color: var(--accent-green); font-size: 0.75rem;">Verified Provenance</span>
        </div>
        <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">
          <strong>Device:</strong> ${result.entity.brand} ${result.entity.model}<br>
          <strong>Location:</strong> ${result.entity.location} · <strong>Manufactured:</strong> 2024 (2 yrs old)<br>
          <strong>Warranty:</strong> ${result.warranty.provider} (Active until ${result.warranty.valid_until})<br>
          <span style="font-size: 0.72rem; color: var(--alexa-cyan);">📍 Provenance: photo_inspection:tag_scan</span>
        </div>
      </div>
    `);

    speakMessage(responseText);
  } catch (err) {
    console.error("Device registration failed:", err);
  }
}

/**
 * 6. Privacy & Provenance Inspector
 */
async function openPrivacyInspector() {
  const drawer = document.getElementById("privacy-inspector");
  drawer.classList.toggle("hidden");

  if (!drawer.classList.contains("hidden")) {
    try {
      const res = await fetch(`${API_BASE}/api/call`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "list_entities", arguments: {} })
      });
      const data = await res.json();
      const entities = data.result[0].entities;
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
    } catch (err) {
      console.error("Failed to load entities:", err);
    }
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
