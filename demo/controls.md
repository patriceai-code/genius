# GENIUS — Demo Production & Hardware Controls

## 1. Hardware Checklist

- [ ] **Display Device (Multimodal Surface):** iPad / Tablet (or secondary monitor in horizontal Echo Show orientation) displaying `http://localhost:8000/client/index.html` with the mandatory header **"ALEXA+ PREVIEW DEVICE SIMULATOR"** clearly visible at all times.
- [ ] **Audio Output:** Device speakers active with audible volume for live Amazon Polly Neural TTS (`Joanna`) streaming.
- [ ] **Physical Chirp Trigger:** Click **"Test Real Recording (Bloofrzo CC0)"** or **"Simulate 3:14 AM Chirp"** (which plays the physical audio recording aloud through the audio pipeline and triggers live in-flight FFT matching).
- [ ] **Video Capture:** Screen recorder (OBS / QuickTime) capturing the tablet screen, or camera framed directly on the mounted tablet device in a home environment. Zero unlabeled mockups.


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
