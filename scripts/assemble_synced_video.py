"""
Assemble the synchronized GENIUS official demo video beat-by-beat using FFmpeg.
Outputs:
  - demo_production/genius_official_demo.mp4
  - ~/Videos/genius_official_demo.mp4
  - demo_production/verification_frames/*.jpg
"""
import json
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(".").resolve()
GRAPHICS_DIR = BASE_DIR / "demo_production" / "graphics"
UI_CLIPS_DIR = BASE_DIR / "demo_production" / "ui_clips"
SYNCED_CLIPS_DIR = BASE_DIR / "demo_production" / "synced_clips"
VERIFY_DIR = BASE_DIR / "demo_production" / "verification_frames"

SYNCED_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
VERIFY_DIR.mkdir(parents=True, exist_ok=True)

FINAL_OUTPUT = BASE_DIR / "demo_production" / "genius_official_demo.mp4"
VIDEOS_FOLDER_OUTPUT = Path.home() / "Videos" / "genius_official_demo.mp4"


def run_ffmpeg(cmd: list[str], desc: str = ""):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"FFmpeg Error in {desc}:\n{res.stderr[-800:]}")
        raise RuntimeError(f"FFmpeg command failed: {desc}")
    print(f"  [OK] {desc}", flush=True)


def assemble_all():
    manifest_path = BASE_DIR / "demo_production" / "beat_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        beats = json.load(f)

    concat_files = []
    elapsed = 0.0

    for idx, b in enumerate(beats, 1):
        beat_id = b["id"]
        dur = float(b["duration"])
        audio_file = Path(b["audio_file"])
        v_type = b["visual_type"]
        v_file = b["visual_file"]

        video_clip = SYNCED_CLIPS_DIR / f"{idx:02d}_{beat_id}_v.mp4"
        final_clip = SYNCED_CLIPS_DIR / f"{idx:02d}_{beat_id}_final.mp4"

        print(f"\n[{idx}/{len(beats)}] Rendering {beat_id} ({dur:.2f}s, {v_type})", flush=True)

        if v_type == "still":
            img_path = GRAPHICS_DIR / v_file
            cmd_v = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(img_path),
                "-t", f"{dur:.3f}",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-s", "1920x1080",
                str(video_clip),
            ]
            run_ffmpeg(cmd_v, f"Render still {beat_id}")
        elif v_type == "ui_clip":
            src_clip = UI_CLIPS_DIR / v_file
            cmd_v = [
                "ffmpeg", "-y",
                "-i", str(src_clip),
                "-t", f"{dur:.3f}",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,tpad=stop_mode=clone:stop_duration=3",
                "-t", f"{dur:.3f}",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(video_clip),
            ]
            run_ffmpeg(cmd_v, f"Render UI clip {beat_id}")
        else:
            raise ValueError(f"Unknown visual_type: {v_type}")

        cmd_merge = [
            "ffmpeg", "-y",
            "-i", str(video_clip),
            "-i", str(audio_file),
            "-filter_complex", f"[1:a]apad=whole_dur={dur:.3f}[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-ar", "48000",
            "-b:a", "192k",
            "-t", f"{dur:.3f}",
            str(final_clip),
        ]
        run_ffmpeg(cmd_merge, f"Merge audio+video {beat_id}")
        concat_files.append((final_clip, beat_id, elapsed + dur * 0.65))
        elapsed += dur

    # Concatenate all beats into master MP4
    concat_txt = SYNCED_CLIPS_DIR / "synced_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cf, _, _ in concat_files:
            f.write(f"file '{cf.name}'\n")

    cmd_master = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(FINAL_OUTPUT),
    ]
    run_ffmpeg(cmd_master, "Master video concatenation")

    # Copy to ~/Videos/genius_official_demo.mp4
    try:
        VIDEOS_FOLDER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FINAL_OUTPUT, VIDEOS_FOLDER_OUTPUT)
    except Exception as e:
        print(f"Note: could not copy to Videos folder: {e}")

    # Extract verification frames from each beat
    for idx, (_, beat_id, mid_ts) in enumerate(concat_files, 1):
        out_jpg = VERIFY_DIR / f"{idx:02d}_{beat_id}.jpg"
        cmd_frame = [
            "ffmpeg", "-y",
            "-ss", f"{mid_ts:.2f}",
            "-i", str(FINAL_OUTPUT),
            "-frames:v", "1",
            "-q:v", "2",
            str(out_jpg),
        ]
        subprocess.run(cmd_frame, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    size_mb = FINAL_OUTPUT.stat().st_size / (1024 * 1024)
    print("\n=====================================================================")
    print("SUCCESS! GENIUS Official Demo Video Assembled:")
    print(f"  -> {FINAL_OUTPUT}")
    print(f"  -> {VIDEOS_FOLDER_OUTPUT}")
    print(f"  -> Duration: {elapsed:.2f}s ({int(elapsed // 60)}m {int(elapsed % 60)}s) | Size: {size_mb:.2f} MB")
    print("=====================================================================")


if __name__ == "__main__":
    assemble_all()
