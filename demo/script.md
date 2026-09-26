# GENIUS — 90-Second Demo Video Script
**Hackathon Rule Compliance:** Under 3 minutes, English, labeled simulation visible at all times.

---

### Timing & Stage Cue Sheet

| Timestamp | Story Beat | Device & Staging | Action & Speech | Visual Surface / Card |
|---|---|---|---|---|
| **0:00 – 0:15** | **The Problem & Setup** | Camera on Mounted Tablet Simulator (Echo Show style) | *"It’s 3:14 AM and something in your home is chirping. Is it smoke? Carbon monoxide? Low battery? For ten thousand years, houses have known what's wrong, but could never say it. This is GENIUS."* | Tablet displays clean Home Dashboard with mandatory header: **"ALEXA+ PREVIEW DEVICE SIMULATOR"**. |
| **0:15 – 0:35** | **The Acoustic Diagnosis** | User triggers via Simulator (or plays physical audio at mic) | **User:** *"Alexa, what's that sound?"*<br>*(Physical 30s Kidde chirp plays aloud)*<br>**GENIUS (Polly Neural Voice):** *"That's your hallway Carbon Monoxide detector's end-of-life chirp — not a low battery. Sensor expired after 7 years. I've prepared a replacement order proposal for your review."* | **Acoustic Evidence Card** renders with 30s interval marker, 3.2 kHz peak frequency, and Kidde manual §4.2 citation. |
| **0:35 – 0:50** | **Propose $\rightarrow$ Confirm** | User taps Tablet Simulator | **User:** *"Confirm replacement."*<br>*(Taps 'Confirm Replacement ($34.99)')*<br>**GENIUS:** *"Replacement Kidde unit ordered. Tracking registered in your home graph for proactive follow-up."* | Proposal card status transitions to **Confirmed & Dispatched** (Order Ref: AMZN-2026-94819). |
| **0:50 – 1:10** | **The House Speaks First (Proactive Push)** | Unprompted Server Event via SSE | *(No user interaction — amber banner slides down automatically, Polly neural voice speaks)*<br>**GENIUS:** *"Your replacement carbon monoxide alarm just arrived on your front porch. Would you like me to walk you through replacing the hallway unit?"* | Banner renders with interactive **"Walk me through replacement"** button. User clicks; step-by-step guidance displays. |
| **1:10 – 1:25** | **The Privacy & Trust Surface** | User taps Privacy Surface on Tablet | **User:** *"Where did you learn this?"*<br>Opens **What Does GENIUS Know?** inspector showing every fact tagged with its verifiable provenance (manual URL, acoustic DSP) and **Zero Raw Audio Persistence** badge. | Shows category consent toggles and proof that acoustic processing ran FFT in volatile RAM and immediately discarded raw audio. |
| **1:25 – 1:30** | **The Close** | Tablet & Title Card | *"GENIUS — every place has a genius. Yours finally speaks."* | Final title card: MCP Spec 2025-11-25 · Streamable HTTP · GitHub open source. |
