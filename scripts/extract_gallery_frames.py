"""
Extract exactly 15 high-quality 3:2 ratio (1800x1200) images for the Devpost image gallery.
Sources:
- The 5 presentation graphics in demo_production/graphics/
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

def crop_or_pad_to_3_2(src_path: str, dst_path: str, target_size=(1800, 1200)):
    with Image.open(src_path) as im:
        w, h = im.size
        target_ratio = target_size[0] / target_size[1]
        current_ratio = w / h

        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            im_cropped = im.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            im_cropped = im.crop((0, top, w, top + new_h))

        im_resized = im_cropped.resize(target_size, Image.Resampling.LANCZOS)
        im_resized.save(dst_path, "PNG", optimize=True)

def extract_frame_at(seconds: float, output_path: str):
    cmd = [
        "ffmpeg", "-y", "-ss", str(seconds), "-i", VIDEO_PATH,
        "-frames:v", "1", "-q:v", "1", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main():
    print("Generating 15 gallery images at 1800x1200 (3:2 ratio)...")

    # 1. 5 Presentation Graphics
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
        crop_or_pad_to_3_2(src, dst)
        print(f"  [+] 3:2 Graphic: {dst_name}")

    # 2. 10 UI Video Frames (timestamps from beat_manifest.json)
    # Total video length ~168s
    # Act 1 Still 0:00 - 0:29 (01_intro_title, 02_problem_card)
    # Act 2 UI:
    #   act2_b1_voice_diagnose: starts ~29.65s (card arrives ~35s-45s)
    #   act2_b2_physical_chirp: starts ~49.45s (piezo feature extraction ~55s-62s)
    #   act2_b3_confirm: starts ~65.75s (order dispatched AMZN-2026 ~72s)
    #   act2_b4_proactive_delivery: starts ~77.42s (delivery arrival banner ~82s-86s)
    # Act 3:
    #   act3_b1_architecture: still ~88.7s - 103.9s
    #   act3_b2_freeze_health: starts ~103.9s (freeze alert card, home health, deliberation ~108s-120s)
    # Act 4:
    #   act4_b1_privacy: starts ~122.2s (privacy inspector ~126s-132s)
    #   act4_b2_benchmarks: still ~134.0s
    #   act4_b3_outro: still ~151.7s

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
        crop_or_pad_to_3_2(tmp_raw, final_dst)
        if os.path.exists(tmp_raw):
            os.remove(tmp_raw)
        print(f"  [+] 3:2 UI Frame ({sec}s): {filename}")

    print(f"\nAll 15 gallery images successfully generated in:\n{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
