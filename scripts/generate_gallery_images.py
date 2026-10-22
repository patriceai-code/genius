"""
Capture 15 high-resolution (3:2 ratio) gallery screenshots of the GENIUS simulator and architecture graphics.
Aspect ratio: 3:2 (1800 x 1200 px).
"""

import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gallery_submission")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLIENT_URL = f"file:///{os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'index.html')).replace(os.sep, '/')}"

def crop_or_pad_to_3_2(image_path: str, output_path: str, target_size=(1800, 1200)):
    with Image.open(image_path) as im:
        # Resize/crop to exactly 3:2 (target_size)
        w, h = im.size
        target_ratio = target_size[0] / target_size[1]
        current_ratio = w / h

        if current_ratio > target_ratio:
            # Too wide, crop width
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            im_cropped = im.crop((left, 0, left + new_w, h))
        else:
            # Too tall, crop height
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            im_cropped = im.crop((0, top, w, top + new_h))

        im_resized = im_cropped.resize(target_size, Image.Resampling.LANCZOS)
        im_resized.save(output_path, "PNG", optimize=True)

def main():
    print(f"Generating 15 gallery images at 1800x1200 (3:2 ratio)...")
    
    # Process the 5 presentation graphics first
    graphics_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_production", "graphics")
    graphic_files = [
        ("01_intro_title.png", "01_genius_home_world_model_title.png"),
        ("02_problem_card.png", "02_the_3_14_am_chirping_crisis.png"),
        ("03_architecture_math.png", "03_architecture_and_physics_math.png"),
        ("04_benchmarks_beepdb.png", "04_empirical_benchmarks_and_beepdb.png"),
        ("05_outro_business.png", "05_commercial_viability_and_business_model.png"),
    ]

    for src_name, dst_name in graphic_files:
        src_path = os.path.join(graphics_dir, src_name)
        dst_path = os.path.join(OUTPUT_DIR, dst_name)
        if os.path.exists(src_path):
            crop_or_pad_to_3_2(src_path, dst_path)
            print(f"  [+] Saved {dst_name}")

    # Capture 10 live simulator views using Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 3:2 viewport
        page = browser.new_page(viewport={"width": 1800, "height": 1200})
        page.goto(CLIENT_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # 06: Default Home Dashboard Overview
        p06 = os.path.join(OUTPUT_DIR, "06_simulator_dashboard_overview.png")
        page.screenshot(path=p06)
        print("  [+] Saved 06_simulator_dashboard_overview.png")

        # 07: 3:14 AM Chirp Analysis & Acoustic Evidence Card
        page.click("button:has-text('3:14 AM Chirp')")
        time.sleep(1)
        p07 = os.path.join(OUTPUT_DIR, "07_acoustic_evidence_card_diagnosis.png")
        page.screenshot(path=p07)
        print("  [+] Saved 07_acoustic_evidence_card_diagnosis.png")

        # 08: Confirmed Action & Amazon Order Dispatch
        # Click confirm button on card
        confirm_btn = page.locator("button:has-text('Confirm Replacement')")
        if confirm_btn.count() > 0:
            confirm_btn.first.click()
            time.sleep(1)
        p08 = os.path.join(OUTPUT_DIR, "08_propose_confirm_order_dispatched.png")
        page.screenshot(path=p08)
        print("  [+] Saved 08_propose_confirm_order_dispatched.png")

        # 09: Proactive Delivery Push Notification
        page.click("button:has-text('Delivery Push')")
        time.sleep(1)
        p09 = os.path.join(OUTPUT_DIR, "09_proactive_sse_delivery_arrival.png")
        page.screenshot(path=p09)
        print("  [+] Saved 09_proactive_sse_delivery_arrival.png")

        # 10: Step-by-Step Replacement Walkthrough
        walk_btn = page.locator("button:has-text('Walk me through replacement')")
        if walk_btn.count() > 0:
            walk_btn.first.click()
            time.sleep(1)
        p10 = os.path.join(OUTPUT_DIR, "10_interactive_replacement_walkthrough.png")
        page.screenshot(path=p10)
        print("  [+] Saved 10_interactive_replacement_walkthrough.png")

        # 11: Real Physical Smoke Detector Piezo (Bloofrzo CC0)
        page.click("button:has-text('Real Piezo (CC0)')")
        time.sleep(1)
        p11 = os.path.join(OUTPUT_DIR, "11_physical_piezo_dsp_frequency_extraction.png")
        page.screenshot(path=p11)
        print("  [+] Saved 11_physical_piezo_dsp_frequency_extraction.png")

        # 12: Continuous Fleet Home Health Dashboard
        page.click("button:has-text('Home Health')")
        time.sleep(1)
        p12 = os.path.join(OUTPUT_DIR, "12_continuous_weibull_home_health_fleet.png")
        page.screenshot(path=p12)
        print("  [+] Saved 12_continuous_weibull_home_health_fleet.png")

        # 13: Amazon Bedrock Nova Pro Specialist Deliberation
        page.click("button:has-text('Deliberation')")
        time.sleep(1)
        p13 = os.path.join(OUTPUT_DIR, "13_amazon_bedrock_nova_pro_tco_deliberation.png")
        page.screenshot(path=p13)
        print("  [+] Saved 13_amazon_bedrock_nova_pro_tco_deliberation.png")

        # 14: Predictive Thermodynamic Building Freeze Alert
        page.click("button:has-text('Freeze Alert')")
        time.sleep(1)
        p14 = os.path.join(OUTPUT_DIR, "14_predictive_freeze_counterfactual_alert.png")
        page.screenshot(path=p14)
        print("  [+] Saved 14_predictive_freeze_counterfactual_alert.png")

        # 15: Privacy Surface & Ephemeral Zero Retention Inspector
        page.click("button:has-text('Privacy Surface')")
        time.sleep(1)
        p15 = os.path.join(OUTPUT_DIR, "15_privacy_surface_provenance_inspector.png")
        page.screenshot(path=p15)
        print("  [+] Saved 15_privacy_surface_provenance_inspector.png")

        browser.close()

    print(f"\nSuccessfully generated all 15 gallery images in:\n{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
