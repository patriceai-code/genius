"""
beepdb Command-Line Interface (CLI)
Query hardware acoustic signatures directly from your terminal.
"""

import argparse
import json
import os
import sys
from .core import match_beep, match_description, search_signatures


def main():
    parser = argparse.ArgumentParser(
        description="beepdb — Open Database of Hardware Acoustic Signatures & Diagnostic Beep Codes"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Match / Lookup command helper
    def add_match_args(p):
        p.add_argument("--cadence", "-c", dest="cadence", type=float, help="Chirp interval in seconds (e.g. 30, 45, 60)")
        p.add_argument("--interval", "-i", dest="interval", type=float, help="Alias for --cadence (seconds)")
        p.add_argument("--freq", "-f", type=float, required=True, help="Peak frequency in Hz (e.g. 3200, 4000)")
        p.add_argument("--dur", "-d", type=float, default=80.0, help="Pulse duration in ms (default: 80)")
        p.add_argument("--json", action="store_true", help="Output in raw JSON format")

    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Identify device by chirp interval & frequency")
    add_match_args(lookup_parser)

    # Match command (alias for lookup)
    match_parser = subparsers.add_parser("match", help="Identify device by chirp interval & frequency (alias for lookup)")
    add_match_args(match_parser)

    # Describe command (voice-native spoken description matching)
    desc_parser = subparsers.add_parser("describe", help="Match spoken description (interval, brand, pitch) without audio")
    desc_parser.add_argument("--interval", "-i", type=float, required=True, help="Chirp interval in seconds (e.g. 30)")
    desc_parser.add_argument("--brand", "-b", type=str, help="Optional manufacturer brand (e.g. Kidde)")
    desc_parser.add_argument("--hint", type=str, help="Optional device class hint (e.g. co_detector)")
    desc_parser.add_argument("--pitch", "-p", type=str, default="high", help="Perceived pitch: high or low")
    desc_parser.add_argument("--json", action="store_true", help="Output in raw JSON format")

    # Corpus command
    corpus_parser = subparsers.add_parser("corpus", help="List bundled CC0/CC-BY physical & ESC-50 reference audio clips")
    corpus_parser.add_argument("--json", action="store_true", help="Output manifest in raw JSON format")

    # List command
    list_parser = subparsers.add_parser("list", help="List and search verified hardware beep signatures")
    list_parser.add_argument("--brand", "-b", type=str, help="Filter by brand (e.g. Kidde, First Alert)")
    list_parser.add_argument("--class", "-k", dest="device_class", type=str, help="Filter by device class (e.g. co_detector, smoke_detector)")
    list_parser.add_argument("--meaning", "-m", type=str, help="Filter by meaning (e.g. end_of_life, low_battery)")

    args = parser.parse_args()

    if args.command in ("lookup", "match"):
        interval_val = args.cadence if args.cadence is not None else args.interval
        if interval_val is None:
            parser.error("Either --cadence (-c) or --interval (-i) is required for lookup/match.")

        match = match_beep(interval_s=interval_val, peak_freq_hz=args.freq, duration_ms=args.dur)
        if not match:
            print("No matching hardware signature found in beepdb.", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(match, indent=2))
        else:
            print("\n[MATCH] beepdb Acoustic Match Result:")
            print(f"  Device:     {match['brand']} {match['device_class'].replace('_', ' ').title()}")
            print(f"  Meaning:    {match['meaning'].replace('_', ' ').title()} ({match['severity'].upper()})")
            print(f"  Confidence: {int(match['confidence'] * 100)}%")
            print(f"  Action:     {match['action']}")
            print(f"  Source:     {match['source_url']}\n")

    elif args.command == "describe":
        match = match_description(
            interval_s=args.interval,
            brand=args.brand,
            device_hint=args.hint,
            pitch=args.pitch,
        )
        if not match:
            print("No matching hardware signature found in beepdb.", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(match, indent=2))
        else:
            print("\n[DESCRIBE] beepdb Conversational Match Result:")
            print(f"  Device:     {match['brand']} {match['device_class'].replace('_', ' ').title()}")
            print(f"  Meaning:    {match['meaning'].replace('_', ' ').title()} ({match['severity'].upper()})")
            print(f"  Confidence: {int(match['confidence'] * 100)}%")
            print(f"  Action:     {match['action']}\n")

    elif args.command == "corpus":
        manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "corpus", "manifest.json")
        if not os.path.exists(manifest_path):
            print("Corpus manifest not found.", file=sys.stderr)
            sys.exit(1)
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if args.json:
            print(json.dumps(manifest, indent=2))
        else:
            print(f"\n{manifest['dataset_name']} ({manifest['license_policy']}):")
            print(f"  Calibrated Smoke Piezos: {len(manifest['calibrated_smoke_piezos'])} clips")
            print(f"  Hardware Tone DSP Clips: {len(manifest['hardware_tone_dsp_checks'])} clips")
            print(f"  ESC-50 Domestic Clips:   {len(manifest['esc50_domestic_non_alarm_clips'])} clips\n")

    elif args.command == "list":
        results = search_signatures(brand=args.brand, device_class=args.device_class, meaning=args.meaning)
        print(f"\nbeepdb Database ({len(results)} signatures):")
        print(f"{'Brand':<15} {'Device Class':<22} {'Cadence':<10} {'Freq':<10} {'Meaning':<20}")
        print("-" * 80)
        for r in results:
            print(f"{r.brand:<15} {r.device_class:<22} {str(r.signature_interval_s)+'s':<10} {str(int(r.peak_freq_hz))+'Hz':<10} {r.meaning:<20}")
        print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
