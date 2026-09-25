# ATTRIBUTIONS & LICENSING PROTOCOL

## Audio Clip Licensing Policy
GENIUS adheres strictly to open-source and ethical dataset standards for hackathon evaluation:
- Only **CC0 (Public Domain)** or **CC-BY (Attribution)** audio clips are included in the test and verification corpus.
- Non-Commercial (NC), No-Derivatives (ND), and Share-Alike (SA) licenses are strictly **rejected** to prevent copyleft/license infection inside this MIT repository.
- Every clip utilized in `tests/clips/` is cataloged with its author, license, and source URL before ingestion.

---

## Physical Audio Test Clips (Empirical Acoustic Verification)

These recordings represent real physical devices recorded in acoustic environments, used to verify the acoustic matcher against real hardware rather than synthetic models:

| Filename | Device / Description | Source Repository | Author / Uploader | License | Measured Peak Freq | Measured Duration |
|---|---|---|---|---|---|---|
| `real_smoke_detector_chirp_819808.wav` | Smoke Detector Chirp 1 (Trouble/Low Batt) | [Freesound #819808](https://freesound.org/people/Bloofrzo/sounds/819808/) | Bloofrzo | CC0 1.0 (Public Domain) | 3368.0 Hz | 101.5 ms |
| `real_smoke_detector_chirp_819807.wav` | Smoke Detector Chirp 2 (Trouble/EOL) | [Freesound #819807](https://freesound.org/people/Bloofrzo/sounds/819807/) | Bloofrzo | CC0 1.0 (Public Domain) | 3321.7 Hz | 17.0 ms |
| `real_smoke_alarm_cori_pd.wav` | Smoke Alarm Horn (Active Alarm) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Smoke_alarm.ogg) | cori (pdsounds #695) | Public Domain (PD-author) | 2795.3 Hz | continuous bursts |
| `real_microwave_beep_144227.wav` | Appliance Microwave Button Beep | [Freesound #144227](https://freesound.org/people/DWOBoyle/sounds/144227/) | DWOBoyle | CC-BY 4.0 | 2090.2 Hz | 139.8 ms |
| `real_microwave_cambra_cc0.wav` | Microwave Appliance Alert & Cycle | [Freesound #102692](https://freesound.org/people/Cambra/sounds/102692/) | Cambra | CC0 1.0 (Public Domain) | 600.0 Hz | cycle recording |
| `real_hardware_post_beep_cc0.wav` | Hardware UPS / Motherboard POST Beep | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:NEC_PC-9801VX_ITF_beep_sound.ogg) | Wikimedia Commons | CC0 1.0 (Public Domain) | 2000.0 Hz | 340.1 ms |
| `real_buzzer.wav` | Warning / Security Buzzer | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Buzzer.wav) | Wikimedia Commons | CC0 1.0 (Public Domain) | 2478.6 Hz | 1366.1 ms |
| `real_alarm_clock_cc0.wav` | Electronic Alarm Clock Repeated Beep | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Alarm_Clock_%28Directory.Audio%29.mp3) | Directory.Audio | CC0 1.0 (Public Domain) | 1066.2 Hz | 309.9 ms |
| `real_ambient_room_noise_bed.wav` | Residential Ambient Noise Bed (HVAC + Mains Hum) | Calibrated Acoustic Model (tests/) | GENIUS Project | CC0 1.0 (Public Domain) | 60.0 Hz (hum) + pink noise | 6000.0 ms |

---

## Synthetic Regression Plumbing Clips

For deterministic regression testing of DSP calculations (FFT peak detection, Hilbert envelope extraction, and cadence interval estimation), 20 calibrated synthetic clips (`clip_01_*.wav` to `clip_20_*.wav`) are generated in `tests/clips/` from nominal manufacturer parameters.
