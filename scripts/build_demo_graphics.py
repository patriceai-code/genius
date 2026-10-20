"""
Build high-definition 1920x1080 cinematic graphics cards for the GENIUS official demo video.
Uses Pillow (PIL) + Matplotlib Computer Modern LaTeX (mathtext) for publication-grade math typesetting.
"""
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configure Matplotlib to use authentic Computer Modern TeX math fonts
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "serif"

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


def render_latex(latex_str: str, fontsize: int = 22, color_rgb=(248, 250, 252), dpi: int = 220) -> Image.Image:
    """Renders a LaTeX math string using Matplotlib Computer Modern font to a tight transparent PIL Image."""
    hex_col = "#{:02x}{:02x}{:02x}".format(*color_rgb[:3])
    fig = plt.figure(figsize=(22, 3.0), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    ax.text(0.5, 0.5, latex_str, fontsize=fontsize, color=hex_col, ha="center", va="center")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=dpi)
    plt.close(fig)
    buf.seek(0)

    im = Image.open(buf).convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3]
    coords = np.argwhere(alpha > 10)
    if coords.size > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        im = im.crop((max(0, x0 - 4), max(0, y0 - 4), min(im.width, x1 + 4), min(im.height, y1 + 4)))
    return im


def paste_centered(base_img: Image.Image, overlay: Image.Image, center_x: int, center_y: int, max_w: int = None):
    if max_w and overlay.width > max_w:
        scale = max_w / overlay.width
        overlay = overlay.resize((int(overlay.width * scale), int(overlay.height * scale)), Image.Resampling.LANCZOS)
    x = int(center_x - overlay.width // 2)
    y = int(center_y - overlay.height // 2)
    base_img.alpha_composite(overlay, (x, y))


def draw_top_simulator_bar(draw: ImageDraw.ImageDraw, section_badge: str, badge_color=ALEXA_CYAN):
    """Draws the top header bar with GENIUS branding and section pill."""
    draw.rectangle([(45, 35), (1875, 1045)], outline=(30, 41, 59), width=2)
    draw.rectangle([(47, 37), (1873, 92)], fill=(13, 19, 33))
    draw.line([(47, 92), (1873, 92)], fill=BORDER_MUTED, width=1)

    draw.rounded_rectangle([(70, 48), (210, 81)], radius=6, fill=(20, 30, 48), outline=ALEXA_CYAN, width=1)
    draw.text((140, 64), "GENIUS MCP", font=get_font(FONT_BOLD, 16), fill=ALEXA_CYAN, anchor="mm")

    draw.rounded_rectangle([(225, 48), (495, 81)], radius=6, fill=badge_color)
    draw.text((360, 64), section_badge, font=get_font(FONT_BOLD, 15), fill=(10, 14, 23), anchor="mm")

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

    draw.rounded_rectangle([(630, 130), (1290, 180)], radius=25, fill=CARD_BG, outline=ALEXA_CYAN, width=2)
    draw.text(
        (960, 155),
        "AMAZON DEVELOPER HACKATHON 2026  ·  ALEXA+ TRACK",
        font=get_font(FONT_BOLD, 18),
        fill=ALEXA_CYAN,
        anchor="mm",
    )

    draw.rounded_rectangle([(730, 215), (1190, 260)], radius=8, fill=(45, 20, 28), outline=CRIMSON, width=1)
    draw.text(
        (960, 237),
        "3:14 AM  ·  HALLWAY CHIRP DETECTED (3.2 kHz / 30s)",
        font=get_font(FONT_MONO, 16),
        fill=(252, 165, 165),
        anchor="mm",
    )

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

    draw.rounded_rectangle([(460, 545), (1460, 615)], radius=12, fill=CARD_ALT, outline=AMAZON_AMBER, width=2)
    draw.text(
        (960, 580),
        '"Every place has a genius. Yours finally speaks."',
        font=get_font(FONT_BOLD, 32),
        fill=AMAZON_AMBER,
        anchor="mm",
    )

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
    """Renders Pillar 1, 2, 3 and Thermodynamic Counterfactual Proof using genuine LaTeX math typesetting."""
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "3-PILLAR WORLD MODEL", ALEXA_CYAN)

    draw.text(
        (960, 138),
        "ZERO BLACK-BOX: DSP, CONTINUOUS PHYSICS & AMAZON BEDROCK",
        font=get_font(FONT_BOLD, 42),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 185),
        "Deterministic local signal processing + continuous reliability math + cloud specialist deliberation",
        font=get_font(FONT_REGULAR, 22),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    pillars = [
        (
            "PILLAR 1: EPHEMERAL DSP (<15ms)",
            "Hilbert Envelope & Volatile Scrub",
            r"$A(t) = \left|\,s(t) + i\,\mathcal{H}\{s(t)\}\,\right|$",
            20,
            [
                "Extracts feature triplet (Δt, f_peak, τ_pulse)",
                "Hann-windowed FFT resolves 3,368 Hz",
                "physical piezo resonance (±350 Hz band)",
                "Immediate RAM zeroing: data.fill(0.0)",
                "0 bytes raw audio on disk or SQLite",
                "Validated on real ESC-50 domestic noises",
            ],
            ALEXA_CYAN,
        ),
        (
            "PILLAR 2: RELIABILITY WORLD MODEL",
            "Weibull Survival & Hazard Rate",
            r"$R(t) = e^{-(t/\eta)^\beta}, \quad h(t) = \frac{\beta}{\eta}\left(\frac{t}{\eta}\right)^{\beta-1}$",
            18,
            [
                "CO Detector: η = 7.0 yr, β = 3.0 wear-out",
                "Carrier Furnace: η = 15.0 yr, β = 2.2 fatigue",
                "Continuous fleet reliability score R_fleet(t)",
                "Replaces static binary device flags",
                "Tracks warranty expiration & lifecycle state",
                "Auditable provenance per graph entity",
            ],
            EMERALD,
        ),
        (
            "PILLAR 3: THERMODYNAMICS & BEDROCK",
            "Heat Loss ODE & Nova Pro TCO",
            r"$\frac{dT_{\mathrm{in}}}{dt} = -\frac{1}{\tau_{\mathrm{pipe}}}(T_{\mathrm{in}} - T_{\mathrm{out}}) + \frac{Q_{\mathrm{furnace}}}{C_{\mathrm{th}}}$",
            18,
            [
                "Simulates unheated pipe cavity cooling",
                "Bedrock Nova Pro 5-yr Repair vs Replace",
                "TCO financial deliberation in 2.64s",
                "Amazon Polly Neural (Joanna) 180ms TTFB",
                "Strict Propose -> Confirm trust boundary",
                "Proactive SSE push when delivery arrives",
            ],
            AMAZON_AMBER,
        ),
    ]

    x = 95
    for title, sub, latex_eq, eq_size, bullets, col in pillars:
        draw.rounded_rectangle([(x, 225), (x + 550, 775)], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 28, 255), title, font=get_font(FONT_BOLD, 21), fill=col)
        draw.text((x + 28, 290), sub, font=get_font(FONT_BOLD, 24), fill=TEXT_WHITE)

        # LaTeX Formula Box
        draw.rounded_rectangle([(x + 22, 332), (x + 528, 422)], radius=10, fill=(10, 15, 26), outline=col, width=1)
        eq_img = render_latex(latex_eq, fontsize=eq_size, color_rgb=col, dpi=220)
        paste_centered(img, eq_img, x + 275, 377, max_w=485)

        y_b = 445
        for b in bullets:
            draw.text((x + 28, y_b), f"•  {b}", font=get_font(FONT_REGULAR, 19), fill=TEXT_LIGHT)
            y_b += 51
        x += 590

    # Bottom Thermodynamic Counterfactual Proof Box with Full LaTeX Equations
    draw.rounded_rectangle([(95, 800), (1825, 1005)], radius=16, fill=CARD_ALT, outline=AMAZON_AMBER, width=2)
    draw.text(
        (135, 832),
        "THERMODYNAMIC COUNTERFACTUAL PROOF  (24°F COLD SNAP · FURNACE TRIPPED · Q_furnace = 0):",
        font=get_font(FONT_BOLD, 20),
        fill=AMAZON_AMBER,
    )

    eq_main = render_latex(
        r"$t_{\mathrm{freeze}} = -\tau_{\mathrm{pipe}}\,\ln\!\left(\frac{T_{\mathrm{freeze}} - T_{\mathrm{out}}}{T_{\mathrm{in}}(0) - T_{\mathrm{out}}}\right) = -16.0\,\ln\!\left(\frac{32 - 24}{68 - 24}\right) = -16.0\,\ln\!\left(\frac{8}{44}\right) = 27.3\;\mathrm{hours} \quad \left(P_{10} = 18.2\;\mathrm{h}\right)$",
        fontsize=19,
        color_rgb=TEXT_WHITE,
        dpi=220,
    )
    paste_centered(img, eq_main, 960, 898, max_w=1650)

    eq_mc = render_latex(
        r"$\mathrm{Monte\;Carlo\;(N=5,000):}\quad P\left(t_{\mathrm{freeze}} \leq 48\mathrm{h} \;\mid\; \tau_{\mathrm{pipe}} \sim \mathrm{Lognormal}(\ln 16,\, 0.3)\right) = 94.1\% \quad |\quad \tau=24\mathrm{h} \rightarrow 66.0\% \quad |\quad \tau=35\mathrm{h} \rightarrow 25.0\%$",
        fontsize=16,
        color_rgb=ALEXA_CYAN,
        dpi=220,
    )
    paste_centered(img, eq_mc, 960, 968, max_w=1650)

    img.save(OUTPUT_DIR / "03_architecture_math.png")
    print("Created 03_architecture_math.png (with LaTeX equations)")


def create_04_benchmarks_beepdb():
    img = Image.new("RGBA", (1920, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_top_simulator_bar(draw, "EMPIRICAL PROOF & ESC-50", EMERALD)

    draw.text(
        (960, 140),
        "REAL HARDWARE, ESC-50 DATASET BENCHMARKS & OPEN-SOURCE BEEPDB",
        font=get_font(FONT_BOLD, 40),
        fill=TEXT_WHITE,
        anchor="mm",
    )
    draw.text(
        (960, 190),
        "Validated on physical Freesound/Wikimedia hardware recordings + peer-reviewed ESC-50 Domestic Dataset (Piczak, ACM MM)",
        font=get_font(FONT_REGULAR, 21),
        fill=TEXT_SLATE,
        anchor="mm",
    )

    # Top 4 KPI Metric Boxes
    kpis = [
        ("13.52 ms", "Total Local Pipeline", "9.80ms DSP + 3.70ms DB", ALEXA_CYAN),
        ("F1 = 1.000", "Ablation vs Baselines", "vs 0.211 Naive ZCR (p<0.001)", EMERALD),
        ("0.0% FPR", "ESC-50 Specificity", "0/6 False Alarms on Home Noise", AMAZON_AMBER),
        ("21 / 21", "Passing Pytest Gates", "0 Bytes Audio on Disk", PURPLE),
    ]
    x = 95
    for val, lbl, sub, col in kpis:
        draw.rounded_rectangle([(x, 235), (x + 405, 420)], radius=14, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 202, 295), val, font=get_font(FONT_BOLD, 44), fill=col, anchor="mm")
        draw.text((x + 202, 355), lbl, font=get_font(FONT_BOLD, 21), fill=TEXT_WHITE, anchor="mm")
        draw.text((x + 202, 390), sub, font=get_font(FONT_REGULAR, 17), fill=TEXT_SLATE, anchor="mm")
        x += 440

    # Left Box: Latency & Accuracy Table
    draw.rounded_rectangle([(95, 455), (940, 990)], radius=16, fill=CARD_BG, outline=BORDER_MUTED, width=2)
    draw.text((130, 490), "SCIENTIFIC ABLATION & ESC-50 BENCHMARK RECEIPTS", font=get_font(FONT_BOLD, 22), fill=ALEXA_CYAN)

    rows = [
        ("[Baseline 1] Naive Zero-Crossing + RMS", "F1 = 0.211", "28.6% Prec · 16.7% Rec · 83.3% FPR"),
        ("[Baseline 2] Narrow FFT (±50 Hz Spec)", "F1 = 0.870", "90.9% Prec · 83.3% Rec · 16.7% FPR"),
        ("[GENIUS Full] Hilbert + ±350 Hz beepdb", "F1 = 1.000", "100% Prec · 100% Rec · 0.0% FPR"),
        ("Physical Piezo Hardware (Freesound CC0)", "100.0% (6/6)", "3,368 Hz measured vs 3,200 Hz nominal"),
        ("ESC-50 Real Domestic Mix (+15 dB SNR)", "100.0% (6/6)", "Vacuum, washer, water, knock, steps"),
        ("ESC-50 Heavy Noise Gate (+6 dB SNR)", "90.0% (9/10)", "Real ESC-50 domestic noise bed"),
        ("20-Device Reference Cadence Table", "95.0% (19/20)", "CO vs Smoke 30s conservative tie-break"),
        ("Local DSP + Scrub + DB Pipeline", "13.52 ms", "9.80ms FFT + 0.005ms scrub + 3.70ms DB"),
        ("Bedrock Nova Pro + Polly Neural/Gen", "2.64s / 180ms", "100% Native AWS AI & Voice Stack"),
    ]
    y = 545
    for name, metric, note in rows:
        col_m = CRIMSON if "0.211" in metric else (AMAZON_AMBER if "0.870" in metric else EMERALD)
        draw.text((130, y), name, font=get_font(FONT_SEMIBOLD, 17), fill=TEXT_WHITE)
        draw.text((515, y), metric, font=get_font(FONT_MONO, 17), fill=col_m)
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

    draw.text((1015, 845), "20 Sourced Hardware Signatures + Real ESC-50 Audio Corpus:", font=get_font(FONT_BOLD, 19), fill=TEXT_WHITE)
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
        "[PASS] 21/21 GENIUS Gates + 5/5 beepdb Gates   ·   [CC0 / CC-BY 4.0] Real Audio",
        font=get_font(FONT_SEMIBOLD, 16),
        fill=EMERALD,
    )

    img.save(OUTPUT_DIR / "04_benchmarks_beepdb.png")
    print("Created 04_benchmarks_beepdb.png (with ESC-50 real dataset benchmarks)")


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

    draw.rounded_rectangle([(95, 575), (1825, 995)], radius=18, fill=CARD_ALT, outline=ALEXA_CYAN, width=2)

    draw.text((960, 640), "GENIUS — THE HOME WORLD MODEL", font=get_font(FONT_BOLD, 48), fill=TEXT_WHITE, anchor="mm")
    draw.text(
        (960, 700),
        '"Every place has a genius. Yours finally speaks."',
        font=get_font(FONT_BOLD, 32),
        fill=AMAZON_AMBER,
        anchor="mm",
    )

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
