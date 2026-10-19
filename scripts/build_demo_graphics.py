"""
Build high-definition 1920x1080 cinematic graphics cards for the GENIUS official demo video.
Uses Pillow (PIL) with clean typography, Amazon Alexa+ cyan/amber accents, and zero text overlap.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("demo_production/graphics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

# Palette
BG_DARK = (9, 13, 22, 255)
CARD_BG = (17, 24, 39)
CARD_ALT = (24, 33, 52)
BORDER_MUTED = (45, 58, 82)
TEXT_WHITE = (248, 250, 252)
TEXT_SLATE = (148, 163, 184)
TEXT_LIGHT = (203, 213, 225)
ALEXA_CYAN = (0, 202, 255)
AMAZON_AMBER = (255, 153, 0)
EMERALD = (16, 185, 129)
CRIMSON = (239, 68, 68)
PURPLE = (168, 85, 247)


def get_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(FONT_REGULAR, size)
        except Exception:
            return ImageFont.load_default()


def draw_top_simulator_bar(draw: ImageDraw.ImageDraw, section_badge: str, badge_color=ALEXA_CYAN):
    """Draws the top header bar with GENIUS branding and section pill."""
    # Outer frame
    draw.rectangle([(45, 35), (1875, 1045)], outline=(30, 41, 59), width=2)
    # Top bar background
    draw.rectangle([(47, 37), (1873, 92)], fill=(13, 19, 33))
    draw.line([(47, 92), (1873, 92)], fill=BORDER_MUTED, width=1)

    # Brand badge
    draw.rounded_rectangle([(70, 48), (210, 81)], radius=6, fill=(20, 30, 48), outline=ALEXA_CYAN, width=1)
    draw.text((140, 64), "GENIUS MCP", font=get_font(FONT_BOLD, 16), fill=ALEXA_CYAN, anchor="mm")

    # Section badge
    draw.rounded_rectangle([(225, 48), (495, 81)], radius=6, fill=badge_color)
    draw.text((360, 64), section_badge, font=get_font(FONT_BOLD, 15), fill=(10, 14, 23), anchor="mm")

    # Right spec indicator
    draw.text(
        (1845, 64),
        "ALEXA+ TRACK  ·  MCP SPEC 2025-11-25  ·  AWS BUILDER  ·  OPEN SOURCE",
        font=get_font(FONT_SEMIBOLD, 14),
        fill=TEXT_SLATE,
        anchor="rm",
    )


def create_01_intro_title():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(45, 35), (1875, 1045)], outline=(30, 41, 59), width=2)
    draw.rectangle([(55, 45), (1865, 1035)], outline=(18, 28, 46), width=1)

    # Top Hackathon Pill
    draw.rounded_rectangle([(630, 130), (1290, 180)], radius=25, fill=CARD_BG, outline=ALEXA_CYAN, width=2)
    draw.text(
        (960, 155),
        "AMAZON DEVELOPER HACKATHON 2026  ·  ALEXA+ TRACK",
        font=get_font(FONT_BOLD, 18),
        fill=ALEXA_CYAN,
        anchor="mm",
    )

    # 3:14 AM Hook Banner
    draw.rounded_rectangle([(730, 215), (1190, 260)], radius=8, fill=(45, 20, 28), outline=CRIMSON, width=1)
    draw.text(
        (960, 237),
        "3:14 AM  ·  HALLWAY CHIRP DETECTED (3.2 kHz / 30s)",
        font=get_font(FONT_MONO, 16),
        fill=(252, 165, 165),
        anchor="mm",
    )

    # Main Title
    draw.text((960, 355), "GENIUS", font=get_font(FONT_BOLD, 118), fill=TEXT_WHITE, anchor="mm")
    draw.text(
        (960, 445),
        "Graph Engine for Networked Infrastructure Understanding & Service",
        font=get_font(FONT_SEMIBOLD, 30),
        fill=ALEXA_CYAN,
        anchor="mm",
    )
    draw.text(
        (960, 495),
        "Self-Hosted MCP Streamable HTTP Server & Persistent Home World Model for Alexa+",
        font=get_font(FONT_REGULAR, 23),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    # Tagline
    draw.rounded_rectangle([(460, 545), (1460, 615)], radius=12, fill=CARD_ALT, outline=AMAZON_AMBER, width=2)
    draw.text(
        (960, 580),
        '"Every place has a genius. Yours finally speaks."',
        font=get_font(FONT_BOLD, 32),
        fill=AMAZON_AMBER,
        anchor="mm",
    )

    # 3 Track / Challenge Cards
    cards = [
        (
            "PRIMARY TRACK: ALEXA+",
            "MCP Spec 2025-11-25 Server",
            "Streamable HTTP + SSE Proactive Push\n12 Strictly Typed Home Graph Tools\nPropose -> Confirm Trust Boundary",
            ALEXA_CYAN,
        ),
        (
            "MINI-CHALLENGE: AWS BUILDER",
            "Amazon Bedrock + Polly + S3",
            "Amazon Nova Pro 5-Yr TCO Deliberation\nMultimodal Appliance Nameplate Vision\nAmazon Polly Neural TTS (Joanna)",
            AMAZON_AMBER,
        ),
        (
            "MINI-CHALLENGE: OPEN SOURCE",
            "beepdb Standalone Package",
            "20 Calibrated Hardware Beep Signatures\nHilbert Envelope + Hann FFT (<15ms)\nMIT Code + CC-BY 4.0 Data License",
            EMERALD,
        ),
    ]

    x = 110
    for header, sub, body, col in cards:
        draw.rounded_rectangle([(x, 670), (x + 530, 960)], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.rectangle([(x + 28, 700), (x + 110, 705)], fill=col)
        draw.text((x + 28, 725), header, font=get_font(FONT_BOLD, 20), fill=col)
        draw.text((x + 28, 758), sub, font=get_font(FONT_BOLD, 24), fill=TEXT_WHITE)
        y_line = 805
        for line in body.split("\n"):
            draw.text((x + 28, y_line), f"•  {line}", font=get_font(FONT_REGULAR, 18), fill=TEXT_LIGHT)
            y_line += 36
        x += 585

    img.save(OUTPUT_DIR / "01_intro_title.png")
    print("Created 01_intro_title.png")


def create_02_problem_card():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "THE 3:14 AM CRISIS", CRIMSON)

    draw.text(
        (960, 145),
        "WHY HOMES FAIL SILENTLY: THE AMBIGUOUS BEEP CRISIS",
        font=get_font(FONT_BOLD, 44),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 198),
        "142M US housing units contain dozens of unmonitored piezo buzzers locked inside obscure PDF manuals",
        font=get_font(FONT_REGULAR, 23),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    stakes = [
        (
            "LIFE-SAFETY CONFUSION",
            "CO End-of-Life vs. Low Battery",
            "CRITICAL SAFETY HAZARD",
            "Homeowners routinely mistake a 30-second\nCO detector End-of-Life chirp for a low\nbattery, swap the 9V cell, and leave a dead\nelectrochemical sensor guarding lethal gas.\n\nSource: CPSC & NFPA Residential Studies",
            CRIMSON,
        ),
        (
            "$12,514 WATER CLAIMS",
            "Unheard Appliance & Leak Alerts",
            ">$15B ANNUAL US LOSSES",
            "Ignored dehumidifier, sump pump, and leak\nsensor chirps lead to catastrophic water\ndamage averaging $12,514 per residential\ninsurance claim.\n\nSource: Insurance Information Institute / ISO",
            AMAZON_AMBER,
        ),
        (
            "$15,000+ PIPE BURSTS",
            "Unmitigated Furnace Lockouts",
            "27.3h FREEZE WINDOW",
            "Aging furnaces locking out during sub-freezing\nnights cool unheated pipe cavities to 32°F in\n27.3 hours, causing $15K-$20K burst pipe\nfloods + $89-$150 diagnostic truck rolls.\n\nSource: State Farm & HomeAdvisor Surveys",
            ALEXA_CYAN,
        ),
    ]

    x = 105
    for title, subtitle, pill, desc, col in stakes:
        draw.rounded_rectangle([(x, 255), (x + 540, 745)], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.rounded_rectangle([(x + 28, 285), (x + 340, 322)], radius=6, fill=(30, 41, 59))
        draw.text((x + 42, 303), pill, font=get_font(FONT_BOLD, 15), fill=col, anchor="lm")
        draw.text((x + 28, 350), title, font=get_font(FONT_BOLD, 28), fill=TEXT_WHITE)
        draw.text((x + 28, 390), subtitle, font=get_font(FONT_SEMIBOLD, 20), fill=col)

        y_text = 445
        for line in desc.split("\n"):
            draw.text((x + 28, y_text), line, font=get_font(FONT_REGULAR, 19), fill=TEXT_LIGHT)
            y_text += 32
        x += 585

    # Bottom Paradigm Shift Banner
    draw.rounded_rectangle([(105, 790), (1815, 985)], radius=16, fill=CARD_ALT, outline=EMERALD, width=2)
    draw.text(
        (960, 845),
        "PARADIGM SHIFT: FROM STATELESS TOOL DRAWER TO PERSISTENT HOME WORLD MODEL",
        font=get_font(FONT_BOLD, 26),
        fill=EMERALD,
        anchor="mm",
    )
    draw.text(
        (960, 895),
        "Basic chatbots guess from prompts. GENIUS extracts physical acoustic features in <15ms, queries manufacturer",
        font=get_font(FONT_REGULAR, 21),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 932),
        "citations in beepdb, tracks Weibull hazard decay R(t), and simulates building thermodynamics before pipes freeze.",
        font=get_font(FONT_REGULAR, 21),
        fill=TEXT_WHITE,
        anchor="mm",
    )

    img.save(OUTPUT_DIR / "02_problem_card.png")
    print("Created 02_problem_card.png")


def create_03_architecture_math():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "3-PILLAR WORLD MODEL", ALEXA_CYAN)

    draw.text(
        (960, 140),
        "ZERO BLACK-BOX: DSP, CONTINUOUS PHYSICS & AMAZON BEDROCK",
        font=get_font(FONT_BOLD, 42),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 190),
        "Deterministic local signal processing + continuous reliability math + cloud specialist deliberation",
        font=get_font(FONT_REGULAR, 22),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    pillars = [
        (
            "PILLAR 1: EPHEMERAL DSP (<15ms)",
            "Hilbert Envelope & Volatile Scrub",
            "A(t) = |s(t) + i · H{s(t)}|",
            [
                "Extracts (Δt_cadence, f_peak, τ_pulse)",
                "Hann-windowed FFT resolves 3,368 Hz",
                "physical piezo drift (±350 Hz band)",
                "Immediate RAM zeroing: data.fill(0.0)",
                "0 bytes raw audio on disk or SQLite",
                "Voice-native diagnose_from_description",
            ],
            ALEXA_CYAN,
        ),
        (
            "PILLAR 2: MATHEMATICAL WORLD MODEL",
            "Weibull Hazard & Thermodynamics",
            "R(t) = exp(-(t/η)^β)  |  dT/dt",
            [
                "CO Detector: η=7.0y, β=3.0 wear-out",
                "Carrier Furnace: η=15.0y, β=2.2 fatigue",
                "Lumped-capacitance pipe cavity model:",
                "dT/dt = -(1/τ_pipe)(T_in - T_out)",
                "At 24°F ambient (τ=16h): freezes in 27.3h",
                "5,000-run Monte Carlo: 94.1% freeze risk",
            ],
            EMERALD,
        ),
        (
            "PILLAR 3: AWS BEDROCK & ALEXA+",
            "Nova Pro Deliberation & SSE Push",
            "amazon.nova-pro-v1:0  +  Polly",
            [
                "Bedrock Nova Pro 5-yr Repair vs Replace",
                "TCO financial deliberation in 2.64s",
                "Multimodal Vision reads appliance tags",
                "Amazon Polly Neural (Joanna) 180ms TTFB",
                "Strict Propose -> Confirm trust gate",
                "Proactive SSE push when delivery arrives",
            ],
            AMAZON_AMBER,
        ),
    ]

    x = 95
    for title, sub, formula, bullets, col in pillars:
        draw.rounded_rectangle([(x, 235), (x + 550, 785)], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 28, 265), title, font=get_font(FONT_BOLD, 21), fill=col)
        draw.text((x + 28, 300), sub, font=get_font(FONT_BOLD, 24), fill=TEXT_WHITE)

        # Formula box
        draw.rounded_rectangle([(x + 25, 345), (x + 525, 405)], radius=8, fill=(12, 18, 30), outline=BORDER_MUTED, width=1)
        draw.text((x + 275, 375), formula, font=get_font(FONT_MONO, 20), fill=col, anchor="mm")

        y_b = 435
        for b in bullets:
            draw.text((x + 28, y_b), f"•  {b}", font=get_font(FONT_REGULAR, 19), fill=TEXT_LIGHT)
            y_b += 52
        x += 590

    # Bottom Thermodynamic Proof Strip
    draw.rounded_rectangle([(95, 815), (1825, 995)], radius=14, fill=CARD_ALT, outline=BORDER_MUTED, width=2)
    draw.text(
        (135, 855),
        "THERMODYNAMIC COUNTERFACTUAL PROOF (24°F COLD SNAP · HEAT OFF):",
        font=get_font(FONT_BOLD, 21),
        fill=AMAZON_AMBER,
    )
    draw.text(
        (135, 900),
        "t_freeze = -τ_pipe · ln((32 - T_out) / (T_in(0) - T_out)) = -16.0 · ln(8 / 44) = 27.3 hours   (10th percentile risk: 18.2 hours)",
        font=get_font(FONT_MONO, 21),
        fill=TEXT_WHITE,
    )
    draw.text(
        (135, 945),
        "Sensitivity Conditioning:   τ_pipe = 16h (Cavity) -> 94.1% Risk   |   τ = 24h -> 66.0% Risk   |   τ = 35h (Envelope) -> 25.0% Risk",
        font=get_font(FONT_REGULAR, 19),
        fill=TEXT_SLATE,
    )

    img.save(OUTPUT_DIR / "03_architecture_math.png")
    print("Created 03_architecture_math.png")


def create_04_benchmarks_beepdb():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "EMPIRICAL PROOF & BEEPDB", EMERALD)

    draw.text(
        (960, 140),
        "REPRODUCIBLE BENCHMARKS & OPEN-SOURCE BEEPDB LIBRARY",
        font=get_font(FONT_BOLD, 42),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 190),
        "Verified via benchmarks/run_benchmarks.py and 19 automated pytest gates on Python 3.11 & 3.12 CI",
        font=get_font(FONT_REGULAR, 22),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    # Top 4 KPI Metric Boxes
    kpis = [
        ("13.52 ms", "Total Local Pipeline", "9.80ms DSP + 3.70ms DB", ALEXA_CYAN),
        ("100% (6/6)", "Physical Piezo Clips", "Bloofrzo CC0 Hardware", EMERALD),
        ("90.0% (9/10)", "+6 dB Heavy Noise", "Domestic Room Noise Bed", AMAZON_AMBER),
        ("19 / 19", "Passing Pytest Gates", "0 Bytes Audio on Disk", PURPLE),
    ]
    x = 95
    for val, lbl, sub, col in kpis:
        draw.rounded_rectangle([(x, 235), (x + 405, 420)], radius=14, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 202, 295), val, font=get_font(FONT_BOLD, 48), fill=col, anchor="mm")
        draw.text((x + 202, 355), lbl, font=get_font(FONT_BOLD, 21), fill=TEXT_WHITE, anchor="mm")
        draw.text((x + 202, 390), sub, font=get_font(FONT_REGULAR, 17), fill=TEXT_SLATE, anchor="mm")
        x += 440

    # Left Box: Latency & Accuracy Table
    draw.rounded_rectangle([(95, 455), (940, 990)], radius=16, fill=CARD_BG, outline=BORDER_MUTED, width=2)
    draw.text((130, 490), "MEASURED PIPELINE RECEIPTS", font=get_font(FONT_BOLD, 24), fill=ALEXA_CYAN)

    rows = [
        ("Synthetic 20-Device Corpus", "95.0% (19/20)", "CO vs Smoke 30s conservative tie-break"),
        ("Physical Piezo Calibration", "100.0% (6/6)", "3,368 Hz measured vs 3,200 Hz nominal"),
        ("Noise Robustness (+15 dB / +6 dB)", "90.0% (9/10)", "Tested across two SNR noise levels"),
        ("Hilbert + Hann FFT Extraction", "9.80 ms", "In-flight volatile RAM processing"),
        ("Volatile Array Scrubbing", "0.005 ms", "data.fill(0.0) + persistence gate test"),
        ("beepdb Signature Lookup", "0.015 ms", "20 devices across 9 categories"),
        ("Home Graph SQLite Write", "3.70 ms", "Auditable provenance + proposals"),
        ("Bedrock Nova Pro Deliberation", "2,640 ms", "Live 5-yr TCO JSON analysis"),
        ("Amazon Polly Neural TTS", "180 ms", "Joanna neural voice stream TTFB"),
    ]
    y = 545
    for name, metric, note in rows:
        draw.text((130, y), name, font=get_font(FONT_SEMIBOLD, 18), fill=TEXT_WHITE)
        draw.text((515, y), metric, font=get_font(FONT_MONO, 18), fill=EMERALD)
        draw.text((665, y), note, font=get_font(FONT_REGULAR, 15), fill=TEXT_SLATE)
        draw.line([(130, y + 32), (910, y + 32)], fill=(30, 41, 59), width=1)
        y += 47

    # Right Box: Open Source beepdb Showcase
    draw.rounded_rectangle([(980, 455), (1825, 990)], radius=16, fill=CARD_BG, outline=EMERALD, width=2)
    draw.text((1015, 490), "OPEN-SOURCE MINI-CHALLENGE: beepdb", font=get_font(FONT_BOLD, 24), fill=EMERALD)
    draw.text(
        (1015, 528),
        "github.com/patriceai-code/beepdb  ·  MIT Code + CC-BY 4.0 Data",
        font=get_font(FONT_MONO, 17),
        fill=TEXT_LIGHT,
    )

    # Terminal CLI mockup
    draw.rounded_rectangle([(1015, 565), (1790, 815)], radius=10, fill=(10, 14, 22), outline=BORDER_MUTED, width=1)
    cli_lines = [
        ("$ pip install git+https://github.com/patriceai-code/beepdb.git", TEXT_SLATE),
        ("$ beepdb match --freq 3200 --interval 30.0", ALEXA_CYAN),
        ("============================================================", BORDER_MUTED),
        ("MATCH FOUND: Kidde KN-COPP-3 (co_detector)", EMERALD),
        ("Meaning    : end_of_life  |  Severity: CRITICAL (99% Match)", AMAZON_AMBER),
        ("Action     : replace_unit;propose_purchase", TEXT_WHITE),
        ("Citation   : kidde.com/.../carbon-monoxide-alarm-beeping/", TEXT_LIGHT),
    ]
    yc = 585
    for line, col in cli_lines:
        draw.text((1035, yc), line, font=get_font(FONT_MONO, 16), fill=col)
        yc += 31

    draw.text((1015, 845), "20 Sourced Hardware Signatures Across 9 Appliance Classes:", font=get_font(FONT_BOLD, 19), fill=TEXT_WHITE)
    draw.text(
        (1015, 880),
        "Kidde · First Alert · Google Nest · X-Sense · Honeywell · FireAngel",
        font=get_font(FONT_REGULAR, 18),
        fill=TEXT_LIGHT,
    )
    draw.text(
        (1015, 912),
        "Samsung · LG · Bosch · Govee · Moen · YoLink · APC · CyberPower · Carrier",
        font=get_font(FONT_REGULAR, 18),
        fill=TEXT_LIGHT,
    )
    draw.text(
        (1015, 950),
        "[PASS] 5/5 Unit & CLI Tests Passing   ·   [OPEN] Community CONTRIBUTING.md Schema",
        font=get_font(FONT_SEMIBOLD, 17),
        fill=EMERALD,
    )

    img.save(OUTPUT_DIR / "04_benchmarks_beepdb.png")
    print("Created 04_benchmarks_beepdb.png")


def create_05_outro_business():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "COMMERCIAL IMPACT & LINKS", AMAZON_AMBER)

    draw.text(
        (960, 140),
        "COMMERCIAL VIABILITY: 4 HIGH-MARGIN REVENUE ENGINES",
        font=get_font(FONT_BOLD, 42),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 190),
        "Transforming Alexa+ from a conversational timer into an indispensable home infrastructure custodian",
        font=get_font(FONT_REGULAR, 22),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    streams = [
        ("45%", "Prime Hardware & Consumables", "1-click verified replacement dispatch\n(Kidde CO $34.99, 9V packs, filters)\nHigh-urgency retail GMV capture", AMAZON_AMBER),
        ("30%", "Insurance Carrier Telemetry", "Mitigates $15B+ freeze & flood claims\nSubsidized Alexa+ partnerships with\nState Farm, Nationwide, and Aviva", ALEXA_CYAN),
        ("15%", "Alexa+ Subscription Retention", "The killer $9.99/mo differentiator:\nprevents $12,500 disasters & decodes\n3:14 AM panic chirps with certainty", EMERALD),
        ("10%", "Warranty Claim Automation", "Auto-files manufacturer claim dossiers\nRecovers $300-$1,500 per appliance\nAuditable home provenance ledger", PURPLE),
    ]

    x = 95
    for pct, title, desc, col in streams:
        draw.rounded_rectangle([(x, 235), (x + 405, 535)], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 202, 295), pct, font=get_font(FONT_BOLD, 54), fill=col, anchor="mm")
        draw.text((x + 202, 355), title, font=get_font(FONT_BOLD, 21), fill=TEXT_WHITE, anchor="mm")
        yb = 400
        for line in desc.split("\n"):
            draw.text((x + 202, yb), line, font=get_font(FONT_REGULAR, 17), fill=TEXT_LIGHT, anchor="mm")
            yb += 30
        x += 440

    # Center Outro Hero Box
    draw.rounded_rectangle([(95, 575), (1825, 995)], radius=18, fill=CARD_ALT, outline=ALEXA_CYAN, width=2)

    draw.text((960, 640), "GENIUS — THE HOME WORLD MODEL", font=get_font(FONT_BOLD, 48), fill=TEXT_WHITE, anchor="mm")
    draw.text(
        (960, 700),
        '"Every place has a genius. Yours finally speaks."',
        font=get_font(FONT_BOLD, 32),
        fill=AMAZON_AMBER,
        anchor="mm",
    )

    # Links Grid
    links = [
        ("PRIMARY REPOSITORY (MIT):", "https://github.com/patriceai-code/genius", ALEXA_CYAN),
        ("OPEN-SOURCE BEEPDB PACKAGE:", "https://github.com/patriceai-code/beepdb", EMERALD),
        ("LIVE AWS S3 CLOUD SIMULATOR:", "http://genius-simulator-115207986956.s3-website.eu-west-2.amazonaws.com", AMAZON_AMBER),
    ]
    yl = 775
    for label, url, col in links:
        draw.text((240, yl), label, font=get_font(FONT_BOLD, 22), fill=col)
        draw.text((650, yl), url, font=get_font(FONT_MONO, 22), fill=TEXT_WHITE)
        yl += 52

    draw.text(
        (960, 960),
        "Built for Amazon Developer Hackathon 2026  ·  Alexa+ Track  ·  AWS Builder  ·  Open Source",
        font=get_font(FONT_SEMIBOLD, 19),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    img.save(OUTPUT_DIR / "05_outro_business.png")
    print("Created 05_outro_business.png")


if __name__ == "__main__":
    create_01_intro_title()
    create_02_problem_card()
    create_03_architecture_math()
    create_04_benchmarks_beepdb()
    create_05_outro_business()
    print("All 5 GENIUS 1080p graphics generated successfully!")
