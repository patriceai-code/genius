# ATTRIBUTIONS & LICENSING PROTOCOL

## Audio Clip Licensing Policy
GENIUS adheres strictly to open-source and ethical dataset standards for hackathon evaluation:
- Only **CC0 (Public Domain)** or **CC-BY (Attribution)** audio clips are included in the test and verification corpus.
- Non-Commercial (NC) and No-Derivatives (ND) licenses are strictly **rejected**.
- Every clip utilized in `tests/clips/` is cataloged with its author, license, and source URL before ingestion.

## Verified Test Corpora & Sources

| Clip ID | Device / Sound | Source / Repository | Author | License | Notes |
|---|---|---|---|---|---|
| `clip_kidde_co_eol_01` | Kidde CO Detector End-of-Life | Synthetic / Calibrated Spec | GENIUS Project | CC0 1.0 | 30s interval, ~3.2kHz, 80ms pulse |
| `clip_firstalert_smoke_lowbatt_01` | First Alert Smoke Low Battery | Synthetic / Calibrated Spec | GENIUS Project | CC0 1.0 | 45s interval, 4.0kHz, 60ms pulse |
| `clip_nest_protect_chirp_01` | Nest Protect Pulse | Synthetic / Calibrated Spec | GENIUS Project | CC0 1.0 | 60s interval, 3.0kHz, 50ms pulse |

*Note: For deterministic automated testing without external copyright dependencies, synthetic calibration clips are generated from published manufacturer frequency specifications.*
