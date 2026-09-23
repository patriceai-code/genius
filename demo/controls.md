# GENIUS — Demo Production & Hardware Controls

## 1. Hardware Checklist

- [ ] **Primary Device (Acoustic & Voice Input):** Amazon Echo (or Echo Show / microphone).
- [ ] **Secondary Device (Proactive Display):** iPad / Tablet or secondary browser monitor running `http://localhost:8000/client/index.html`.
- [ ] **Audio Source:** Mobile phone or secondary speaker ready to play the 30-second Kidde chirp test clip (`tests/clips/clip_01_kidde_co_detector_end_of_life.wav`).
- [ ] **Backup:** Direct on-screen "Simulate 3:14 AM Chirp" button in the simulator deck if room ambient noise interferes.
- [ ] **Video Capture:** Screen recorder (OBS / QuickTime) + camera recording the dual-device desk setup.

---

## 2. Server Startup Command

```powershell
# In c:\Users\zache\GENIUS
.\.venv\Scripts\python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 3. Demo Run-through Sequence

1. **Pre-Show State:**
   - Open `http://localhost:8000/client/index.html`.
   - Verify green status indicator: `Connected to FastMCP`.
   - Ensure audio volume is audible for speech synthesis.

2. **Beat 1: The Chirp Diagnosis**
   - Click **"Simulate 3:14 AM Chirp"** (or play `tests/clips/clip_01_kidde_co_detector_end_of_life.wav` at mic).
   - Observe immediate assistant speech and the **Acoustic Evidence Card**.
   - Point camera at the 30.0s cadence, 3.2 kHz peak frequency, and manufacturer reference.

3. **Beat 2: Action Confirmation**
   - Click **"Confirm Replacement ($34.99)"**.
   - Notice the order confirmation appears with tracking dispatch.

4. **Beat 3: Unprompted Proactive Push**
   - Click **"Proactive Delivery Follow-Up"** (or `/simulate/delivery`).
   - Notice the amber notification banner slides down unprompted with voice readout.
   - Click **"Walk me through replacement"** to demonstrate multimodal guidance.

5. **Beat 4: Privacy Surface**
   - Click **"Privacy Surface"**.
   - Show the green **"Zero Raw Audio Persistence"** badge.
   - Expand the registered hardware entities to show verified provenance tags.

---

## 4. Key Rules Reminders

- **Time Limit:** Video must be strictly under 3:00 (target: ~90s).
- **Language:** English.
- **Simulator Notice:** The top header badge **"ALEXA+ PREVIEW DEVICE SIMULATOR"** must remain clearly visible whenever the web client is on screen.
