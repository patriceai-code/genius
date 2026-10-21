"""
Generate natural human-sounding voiceover (en-US-AndrewNeural via edge-tts with retry)
combined with real Amazon Polly Neural (Joanna) voice responses and real physical piezo chirp audio.
Target total duration: ~2m 25s (comfortably under the 3:00 Devpost limit).
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
import boto3
import edge_tts
from dotenv import load_dotenv

load_dotenv()

AUDIO_DIR = Path("demo_production/audio_synced")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = Path("demo_production/audio_temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

NARRATOR_VOICE = "en-US-AndrewNeural"
POLLY_VOICE = "Joanna"
REAL_CHIRP_WAV = Path("tests/clips/real_smoke_detector_chirp_819808.wav")

BEATS = [
    # --- ACT 1: THE HOOK & PROBLEM ---
    {
        "id": "act1_b1_title",
        "act": 1,
        "visual_type": "still",
        "visual_file": "01_intro_title.png",
        "prepend_chirp": True,
        "narrator_text": (
            "It's 3:14 AM, and something in your house is chirping. Is it smoke? Carbon monoxide? "
            "A dying battery? For ten thousand years, no house could ever say what is wrong. "
            "Meet GENIUS — the Home World Model for Alexa Plus."
        ),
    },
    {
        "id": "act1_b2_problem",
        "act": 1,
        "visual_type": "still",
        "visual_file": "02_problem_card.png",
        "narrator_text": (
            "Across 142 million U.S. homes, unmonitored alarms and appliances communicate only through "
            "ambiguous beeps. Mistaking a carbon monoxide end-of-life chirp for a low battery is a "
            "lethal safety hazard, while unaddressed leaks and furnace lockouts cause over fifteen "
            "billion dollars in annual residential damage."
        ),
    },

    # --- ACT 2: LIVE SIMULATOR DEMO ---
    {
        "id": "act2_b1_voice_diagnose",
        "act": 2,
        "visual_type": "ui_clip",
        "visual_file": "ui_01_diagnose.mp4",
        "narrator_text": (
            "In our labeled Alexa Plus Device Simulator, connected live to our self-hosted "
            "Model Context Protocol server over Streamable HTTP, a homeowner asks about a 30-second "
            "hallway chirp. GENIUS matches beep-D-B and renders an Acoustic Evidence Card."
        ),
        "polly_text": (
            "That's your hallway Carbon Monoxide detector's end-of-life chirp — not a low battery. "
            "The sensor expired after seven years."
        ),
    },
    {
        "id": "act2_b2_physical_chirp",
        "act": 2,
        "visual_type": "ui_clip",
        "visual_file": "ui_02_real_chirp.mp4",
        "prepend_chirp": True,
        "narrator_text": (
            "For companion edge microphones, GENIUS also ingests raw audio via hear-sound — running a "
            "Hilbert envelope and Hann F-F-T in under 10 milliseconds to catch physical piezo resonance "
            "at 3,368 Hertz, while immediately scrubbing raw audio from volatile RAM."
        ),
    },
    {
        "id": "act2_b3_confirm",
        "act": 2,
        "visual_type": "ui_clip",
        "visual_file": "ui_03_confirm.mp4",
        "narrator_text": (
            "Under our strict Propose-to-Confirm trust boundary, GENIUS never executes purchases autonomously. "
            "Only when the homeowner explicitly confirms does GENIUS dispatch the replacement order and "
            "schedule a proactive follow-up."
        ),
    },
    {
        "id": "act2_b4_proactive_delivery",
        "act": 2,
        "visual_type": "ui_clip",
        "visual_file": "ui_04_delivery.mp4",
        "narrator_text": (
            "When the replacement arrives, the house speaks first via unprompted Server-Sent Events."
        ),
        "polly_text": (
            "Your replacement carbon monoxide alarm just arrived on your front porch. "
            "Would you like me to walk you through replacing the hallway unit?"
        ),
    },

    # --- ACT 3: MATHEMATICAL WORLD MODEL, BEDROCK & THERMODYNAMICS ---
    {
        "id": "act3_b1_architecture",
        "act": 3,
        "visual_type": "still",
        "visual_file": "03_architecture_math.png",
        "narrator_text": (
            "Under the hood, GENIUS is not a black-box LLM wrapper. It unites deterministic signal "
            "processing with a continuous mathematical world model — tracking equipment wear-out via "
            "two-parameter Weibull hazard distributions and simulating building heat loss with "
            "lumped-capacitance differential equations."
        ),
    },
    {
        "id": "act3_b2_freeze_health",
        "act": 3,
        "visual_type": "ui_clip",
        "visual_file": "ui_05_freeze_health.mp4",
        "narrator_text": (
            "When outdoor temperatures drop to 24 degrees with an aging Carrier furnace, our simulation "
            "projects unheated pipe cavities reaching freezing in 27.3 hours — a 94.1 percent Monte Carlo "
            "freeze risk — triggering a proactive warning, fleet reliability scorecard, and live Amazon "
            "Bedrock Nova Pro repair-versus-replace deliberation."
        ),
    },

    # --- ACT 4: PRIVACY, OPEN SOURCE BEEPDB, BENCHMARKS & OUTRO ---
    {
        "id": "act4_b1_privacy",
        "act": 4,
        "visual_type": "ui_clip",
        "visual_file": "ui_06_privacy.mp4",
        "narrator_text": (
            "To eliminate smart-home surveillance anxiety, our privacy inspector shows the exact provenance "
            "of every stored fact, backed by an automated test verifying that zero bytes of raw audio ever "
            "touch disk or SQLite."
        ),
    },
    {
        "id": "act4_b2_benchmarks_beepdb",
        "act": 4,
        "visual_type": "still",
        "visual_file": "04_benchmarks_beepdb.png",
        "narrator_text": (
            "Every claim is backed by transparent, reproducible tests: a 13.52 millisecond local pipeline, "
            "95 percent accuracy on our 20-device synthetic cadence table, a 12-trial E-S-C-50 domestic "
            "noise smoke test where Hann F-F-T recovers 6 of 6 peaks versus 1 of 6 for naive zero-crossing, "
            "22 passing test gates, and our open-source beep-D-B library."
        ),
    },
    {
        "id": "act4_b3_business_outro",
        "act": 4,
        "visual_type": "still",
        "visual_file": "05_outro_business.png",
        "narrator_text": (
            "By uniting Prime replacement fulfillment, insurance loss-mitigation, and warranty recovery, "
            "GENIUS turns Alexa Plus into an indispensable home custodian. GENIUS: every place has a genius. "
            "Yours finally speaks."
        ),
        "extra_padding": 1.2,
    },
]


def get_duration(audio_file: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(res.stdout.strip())


def synthesize_polly(text: str, out_path: Path, voice_id: str = POLLY_VOICE):
    if out_path.exists() and out_path.stat().st_size > 500:
        return
    region = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
    polly = boto3.client("polly", region_name=region)
    res = polly.synthesize_speech(
        Engine="neural",
        OutputFormat="mp3",
        Text=text,
        VoiceId=voice_id,
    )
    with open(out_path, "wb") as f:
        f.write(res["AudioStream"].read())


async def synthesize_narrator_with_retry(text: str, out_path: Path):
    if out_path.exists() and out_path.stat().st_size > 500:
        return
    for attempt in range(4):
        try:
            comm = edge_tts.Communicate(text, NARRATOR_VOICE, rate="+10%")
            await comm.save(str(out_path))
            if out_path.exists() and out_path.stat().st_size > 500:
                return
        except Exception as e:
            print(f"  [Retry {attempt + 1}/4] edge-tts transient error: {e}")
            await asyncio.sleep(1.5 * (attempt + 1))
    # Fallback to Amazon Polly Neural Matthew if edge-tts is unreachable
    print("  [Fallback] Using Amazon Polly Neural (Matthew) for narrator...")
    synthesize_polly(text, out_path, voice_id="Matthew")


def combine_audio_segments(segments: list[Path], out_mp3: Path):
    inputs = []
    filter_parts = []
    for idx, seg in enumerate(segments):
        inputs.extend(["-i", str(seg)])
        # Keep physical chirp and silence at 1.0x; apply crisp 1.13x cadence to speech
        if "real_smoke" in seg.name or "silence" in seg.name:
            filter_parts.append(f"[{idx}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a{idx}];")
        else:
            filter_parts.append(f"[{idx}:a]atempo=1.13,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a{idx}];")

    concat_inputs = "".join(f"[a{i}]" for i in range(len(segments)))
    filter_complex = "".join(filter_parts) + f"{concat_inputs}concat=n={len(segments)}:v=0:a=1[outa]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_mp3),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


async def generate_all_beats():
    print(f"Generating multi-voice audio tracks ({NARRATOR_VOICE} + Amazon Polly {POLLY_VOICE})...", flush=True)

    silence_file = TEMP_DIR / "silence_200ms.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-t", "0.20", str(silence_file),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    manifest = []
    total_dur = 0.0

    for b in BEATS:
        beat_id = b["id"]
        print(f"Synthesizing [{beat_id}]...", flush=True)
        segments = []

        if b.get("prepend_chirp") and REAL_CHIRP_WAV.exists():
            segments.append(REAL_CHIRP_WAV)

        narrator_mp3 = TEMP_DIR / f"{beat_id}_narrator.mp3"
        await synthesize_narrator_with_retry(b["narrator_text"], narrator_mp3)
        segments.append(narrator_mp3)

        if b.get("polly_text"):
            segments.append(silence_file)
            polly_mp3 = TEMP_DIR / f"{beat_id}_polly.mp3"
            synthesize_polly(b["polly_text"], polly_mp3, voice_id=POLLY_VOICE)
            segments.append(polly_mp3)

        out_file = AUDIO_DIR / f"{beat_id}.mp3"
        combine_audio_segments(segments, out_file)

        raw_dur = get_duration(out_file)
        extra = b.get("extra_padding", 0.20)
        dur_padded = round(raw_dur + extra, 3)
        total_dur += dur_padded

        b_data = dict(b)
        b_data["audio_file"] = str(out_file)
        b_data["raw_duration"] = round(raw_dur, 3)
        b_data["duration"] = dur_padded
        manifest.append(b_data)
        print(f"  [OK] {beat_id} -> {raw_dur:.2f}s (padded: {dur_padded:.2f}s)", flush=True)

    manifest_path = Path("demo_production/beat_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved to {manifest_path}", flush=True)
    print(f"Total Video Duration: {total_dur:.2f}s ({int(total_dur // 60)}m {int(total_dur % 60)}s)", flush=True)


if __name__ == "__main__":
    asyncio.run(generate_all_beats())
