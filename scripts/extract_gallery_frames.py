"""
Extract exactly 15 high-quality 3:2 ratio (1800x1200) images for the Devpost image gallery.
Ensures zero clipping:
- 16:9 presentation slides (1920x1080) are letterboxed with dark background into 3:2 (1800x1200)
  so all cards, text, and edges remain 100% visible with zero horizontal cropping.
- 10 precisely timed video frames from demo_production/genius_official_demo.mp4 capturing all key UI views.
"""

import os
import subprocess
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(REPO_ROOT, "gallery_submission")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIDEO_PATH = os.path.join(REPO_ROOT, "demo_production", "genius_official_demo.mp4")
GRAPHICS_DIR = os.path.join(REPO_ROOT, "demo_production", "graphics")

BG_DARK = (10, 15, 29, 255)

def fit_to_3_2_letterbox(src_path: str, dst_path: str, target_size=(1800, 1200)):
    """Pads or scales the image into 3:2 without cropping off any content."""
    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        target_w, target_h = target_size
        scale = min(target_w / im.width, target_h / im.height)
        new_w = int(im.width * scale)
        new_h = int(im.height * scale)
        im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", target_size, BG_DARK)
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        canvas.paste(im_resized, (offset_x, offset_y), im_resized)
        canvas.convert("RGB").save(dst_path, "PNG", optimize=True)

def extract_frame_at(seconds: float, output_path: str):
    cmd = [
        "ffmpeg", "-y", "-ss", str(seconds), "-i", VIDEO_PATH,
        "-frames:v", "1", "-q:v", "1", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main():
    print("Generating 15 gallery images at 1800x1200 (3:2 ratio, zero clipping)...")

    # 1. 5 Presentation Graphics (Letterboxed into 3:2 so edges are never cut off)
    graphic_files = [
        ("01_intro_title.png", "01_genius_home_world_model_title.png"),
        ("02_problem_card.png", "02_the_3_14_am_chirping_crisis.png"),
        ("03_architecture_math.png", "03_architecture_and_physics_math.png"),
        ("04_benchmarks_beepdb.png", "04_empirical_benchmarks_and_beepdb.png"),
        ("05_outro_business.png", "05_commercial_viability_and_business_model.png"),
    ]

    for src_name, dst_name in graphic_files:
        src = os.path.join(GRAPHICS_DIR, src_name)
        dst = os.path.join(OUTPUT_DIR, dst_name)
        fit_to_3_2_letterbox(src, dst)
        print(f"  [+] 3:2 Graphic (zero crop): {dst_name}")

    # 2. 10 UI Video Frames
    ui_frame_specs = [
        (38.0, "06_voice_native_chirp_evidence_card.png"),
        (45.0, "07_manual_citation_and_confidence_score.png"),
        (56.0, "08_physical_piezo_waveform_dsp_extraction.png"),
        (62.0, "09_ephemeral_ram_buffer_zeroing_proof.png"),
        (72.0, "10_propose_confirm_order_dispatched.png"),
        (82.0, "11_proactive_sse_delivery_arrival_banner.png"),
        (108.0, "12_predictive_building_freeze_counterfactual.png"),
        (116.0, "13_weibull_home_health_fleet_matrix.png"),
        (121.0, "14_bedrock_nova_pro_repair_deliberation.png"),
        (128.0, "15_privacy_surface_provenance_inspector.png"),
    ]

    for sec, filename in ui_frame_specs:
        tmp_raw = os.path.join(OUTPUT_DIR, f"temp_{filename}")
        final_dst = os.path.join(OUTPUT_DIR, filename)
        extract_frame_at(sec, tmp_raw)
        fit_to_3_2_letterbox(tmp_raw, final_dst)
        if os.path.exists(tmp_raw):
            os.remove(tmp_raw)
        print(f"  [+] 3:2 UI Frame ({sec}s, zero crop): {filename}")

    print(f"\nAll 15 gallery images successfully generated in:\n{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
