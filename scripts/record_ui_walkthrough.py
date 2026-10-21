"""
Record live 1920x1080 UI walkthrough of the GENIUS Alexa+ Preview Device Simulator
connected to the live self-hosted FastMCP server (http://127.0.0.1:8000/client/index.html).
Slices each UI beat to match the exact duration in demo_production/beat_manifest.json.
"""
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

RAW_DIR = Path("demo_production/ui_raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
UI_CLIPS_DIR = Path("demo_production/ui_clips")
UI_CLIPS_DIR.mkdir(parents=True, exist_ok=True)


def wait_for_server(url: str, timeout: float = 15.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    raise RuntimeError(f"Server at {url} did not become ready within {timeout}s")


def get_beat_durations() -> dict[str, float]:
    manifest_path = Path("demo_production/beat_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        beats = json.load(f)
    return {b["id"]: float(b["duration"]) for b in beats}


def scroll_to_bottom(page):
    page.evaluate(
        """() => {
            const conv = document.querySelector('.conversation-container');
            if (conv) conv.scrollTop = conv.scrollHeight;
            const thread = document.getElementById('chat-thread');
            if (thread) thread.scrollTop = thread.scrollHeight;
        }"""
    )


def record_walkthrough():
    durations = get_beat_durations()

    for old_f in RAW_DIR.glob("*.webm"):
        try:
            old_f.unlink()
        except Exception:
            pass

    # Reset home_graph.db to clean initial seed state before recording
    db_file = Path("home_graph.db")
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass

    print("Starting live FastMCP server on 127.0.0.1:8000...", flush=True)
    server_proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "server.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    segments = {}

    try:
        wait_for_server("http://127.0.0.1:8000/api/config")
        print("FastMCP Server online! Launching Playwright 1080p recorder...", flush=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            t0 = time.monotonic()
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=str(RAW_DIR),
                record_video_size={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            page.goto("http://127.0.0.1:8000/client/index.html", wait_until="networkidle")
            time.sleep(1.5)

            # Stub browser speech synthesis during headless capture
            page.evaluate("window.speakMessage = function(t) { console.log('TTS:', t); };")

            # --- UI BEAT 1: act2_b1_voice_diagnose (ui_01_diagnose.mp4) ---
            b1_dur = durations["act2_b1_voice_diagnose"]
            s1 = time.monotonic() - t0
            print(f"[UI 1] Recording act2_b1_voice_diagnose ({b1_dur:.2f}s)...", flush=True)
            time.sleep(1.0)
            page.evaluate("async () => { await simulateChirp(); }")
            scroll_to_bottom(page)
            time.sleep(2.5)
            page.evaluate("dismissBanner()")
            scroll_to_bottom(page)
            elapsed_1 = (time.monotonic() - t0) - s1
            time.sleep(max(0.5, b1_dur - elapsed_1))
            segments["ui_01_diagnose.mp4"] = (s1, b1_dur)

            # --- UI BEAT 2: act2_b2_physical_chirp (ui_02_real_chirp.mp4) ---
            b2_dur = durations["act2_b2_physical_chirp"]
            s2 = time.monotonic() - t0
            print(f"[UI 2] Recording act2_b2_physical_chirp ({b2_dur:.2f}s)...", flush=True)
            time.sleep(0.8)
            page.evaluate("async () => { await simulateRealChirp(); }")
            scroll_to_bottom(page)
            time.sleep(2.2)
            page.evaluate("dismissBanner()")
            scroll_to_bottom(page)
            elapsed_2 = (time.monotonic() - t0) - s2
            time.sleep(max(0.5, b2_dur - elapsed_2))
            segments["ui_02_real_chirp.mp4"] = (s2, b2_dur)

            # --- UI BEAT 3: act2_b3_confirm (ui_03_confirm.mp4) ---
            b3_dur = durations["act2_b3_confirm"]
            s3 = time.monotonic() - t0
            print(f"[UI 3] Recording act2_b3_confirm ({b3_dur:.2f}s)...", flush=True)
            time.sleep(1.0)
            page.evaluate("async () => { await confirmActionDirect(currentProposalId || 'prop_replace_co_001'); }")
            scroll_to_bottom(page)
            elapsed_3 = (time.monotonic() - t0) - s3
            time.sleep(max(0.5, b3_dur - elapsed_3))
            segments["ui_03_confirm.mp4"] = (s3, b3_dur)

            # --- UI BEAT 4: act2_b4_proactive_delivery (ui_04_delivery.mp4) ---
            b4_dur = durations["act2_b4_proactive_delivery"]
            s4 = time.monotonic() - t0
            print(f"[UI 4] Recording act2_b4_proactive_delivery ({b4_dur:.2f}s)...", flush=True)
            time.sleep(0.6)
            page.evaluate("async () => { await simulateDelivery(); }")
            time.sleep(4.8)
            page.evaluate("handleProactiveAction('walkthrough', 'Walk me through replacement')")
            scroll_to_bottom(page)
            elapsed_4 = (time.monotonic() - t0) - s4
            time.sleep(max(0.5, b4_dur - elapsed_4))
            segments["ui_04_delivery.mp4"] = (s4, b4_dur)

            # --- UI BEAT 5: act3_b2_freeze_health (ui_05_freeze_health.mp4) ---
            b5_dur = durations["act3_b2_freeze_health"]
            s5 = time.monotonic() - t0
            print(f"[UI 5] Recording act3_b2_freeze_health ({b5_dur:.2f}s)...", flush=True)
            time.sleep(0.4)
            page.evaluate("async () => { await simulateFreeze(); }")
            time.sleep(3.6)
            page.evaluate("dismissBanner()")
            page.evaluate("async () => { await fetchHomeHealth(); }")
            scroll_to_bottom(page)
            time.sleep(3.2)
            page.evaluate("async () => { await runDeliberation(); }")
            scroll_to_bottom(page)
            elapsed_5 = (time.monotonic() - t0) - s5
            time.sleep(max(0.5, b5_dur - elapsed_5))
            segments["ui_05_freeze_health.mp4"] = (s5, b5_dur)

            # --- UI BEAT 6: act4_b1_privacy (ui_06_privacy.mp4) ---
            b6_dur = durations["act4_b1_privacy"]
            s6 = time.monotonic() - t0
            print(f"[UI 6] Recording act4_b1_privacy ({b6_dur:.2f}s)...", flush=True)
            time.sleep(0.4)
            page.evaluate("async () => { await openPrivacyInspector(); }")
            time.sleep(8.4)
            page.evaluate("async () => { await openPrivacyInspector(); }")  # close privacy
            time.sleep(0.2)
            page.evaluate("toggleToolExplorer()")  # show 12 MCP tools
            elapsed_6 = (time.monotonic() - t0) - s6
            time.sleep(max(0.5, b6_dur - elapsed_6))
            segments["ui_06_privacy.mp4"] = (s6, b6_dur)

            print("Closing browser context to flush 1080p video...", flush=True)
            context.close()
            browser.close()

    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except Exception:
            server_proc.kill()

    webm_files = sorted(RAW_DIR.glob("*.webm"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not webm_files:
        raise FileNotFoundError("No .webm recording produced by Playwright!")
    raw_webm = webm_files[0]
    print(f"Recorded master UI walkthrough: {raw_webm} ({raw_webm.stat().st_size} bytes)", flush=True)

    for filename, (start_sec, dur_sec) in segments.items():
        out_clip = UI_CLIPS_DIR / filename
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{start_sec:.3f}",
            "-i", str(raw_webm),
            "-t", f"{dur_sec:.3f}",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            str(out_clip),
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"  [OK] Sliced {filename} (ss={start_sec:.2f}s, dur={dur_sec:.2f}s)", flush=True)


if __name__ == "__main__":
    record_walkthrough()
