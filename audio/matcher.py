"""
beepdb Acoustic Matcher
Matches extracted sound features (cadence interval, peak frequency, pulse duration)
against the sourced beepdb database. Returns candidate device, severity, confidence,
and the canonical 3 AM diagnostic explanation.
"""

import os
import csv
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("genius.audio.matcher")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "beepdb", "codes.csv")


class BeepMatch:
    def __init__(
        self,
        device_class: str,
        brand: str,
        meaning: str,
        severity: str,
        action: str,
        source_url: str,
        confidence: float,
        expected_interval_s: float,
        expected_freq_hz: float,
        expected_duration_ms: float
    ):
        self.device_class = device_class
        self.brand = brand
        self.meaning = meaning
        self.severity = severity
        self.action = action
        self.source_url = source_url
        self.confidence = round(confidence, 2)
        self.expected_interval_s = expected_interval_s
        self.expected_freq_hz = expected_freq_hz
        self.expected_duration_ms = expected_duration_ms

    def format_3am_speech(self, location: str = "hallway") -> str:
        """Generates clear, reassuring 3 AM voice readout."""
        loc_phrase = f"in your {location}" if location else "in your home"
        device_title = f"{self.brand} {self.device_class.replace('_', ' ').title()}"

        if self.meaning == "end_of_life":
            return (
                f"That's your {device_title} {loc_phrase} signaling end-of-life, not a low battery. "
                f"Its internal sensor has reached manufacturer expiry. I have prepared a replacement order proposal for your review."
            )
        elif self.meaning == "low_battery":
            return (
                f"That's your {device_title} {loc_phrase} signaling a low battery with a {int(self.expected_interval_s)}-second chirp. "
                f"I can guide you through replacing the battery when you're ready."
            )
        elif self.meaning == "moisture_detected":
            return (
                f"Urgent alert: That's your {device_title} {loc_phrase} detecting water moisture! "
                f"Please inspect the area immediately to prevent water damage."
            )
        elif self.meaning == "door_ajar":
            return (
                f"Your {device_title} door has been left ajar. "
                f"Please verify the seal is closed completely."
            )
        else:
            return (
                f"Identified {device_title} {loc_phrase}: {self.meaning.replace('_', ' ')}. "
                f"Recommended action: {self.action.replace(';', ', ')}."
            )

    def to_dict(self, location: str = "hallway") -> Dict[str, Any]:
        return {
            "device_class": self.device_class,
            "brand": self.brand,
            "meaning": self.meaning,
            "severity": self.severity,
            "action": self.action,
            "confidence": self.confidence,
            "source_url": self.source_url,
            "spoken_summary": self.format_3am_speech(location),
            "expected_specs": {
                "interval_s": self.expected_interval_s,
                "peak_freq_hz": self.expected_freq_hz,
                "duration_ms": self.expected_duration_ms
            }
        }


def load_beepdb(csv_path: str = CSV_PATH) -> List[Dict[str, Any]]:
    """Loads all signatures from codes.csv."""
    rows = []
    if not os.path.exists(csv_path):
        logger.error(f"beepdb file not found at {csv_path}")
        return rows

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "signature_interval_s": float(r["signature_interval_s"]),
                "signature_duration_ms": float(r["signature_duration_ms"]),
                "peak_freq_hz": float(r["peak_freq_hz"]),
                "device_class": r["device_class"],
                "brand": r["brand"],
                "meaning": r["meaning"],
                "severity": r["severity"],
                "action": r["action"],
                "source_url": r["source_url"]
            })
    return rows


def match_acoustic_features(
    interval_s: float,
    peak_freq_hz: float,
    duration_ms: float = 0.0,
    db_rows: Optional[List[Dict[str, Any]]] = None
) -> Optional[BeepMatch]:
    """
    Ranks beepdb rows against detected features and returns the highest-confidence match.
    """
    if db_rows is None:
        db_rows = load_beepdb()

    if not db_rows:
        return None

    best_match = None
    highest_score = -1.0

    for row in db_rows:
        target_interval = row["signature_interval_s"]
        target_freq = row["peak_freq_hz"]
        target_dur = row["signature_duration_ms"]

        # 1. Cadence interval score (cadence bucket)
        if interval_s > 0:
            interval_diff = abs(interval_s - target_interval)
            score_interval = max(0.0, 1.0 - (interval_diff / max(target_interval * 0.25, 2.0)))
        else:
            score_interval = 0.5  # Neutral if interval not captured

        # 2. Resonant peak frequency score (piezo buzzer resonant peak tolerance ~150Hz)
        freq_diff = abs(peak_freq_hz - target_freq)
        score_freq = max(0.0, 1.0 - (freq_diff / 150.0))

        # 3. Pulse duration score (tolerance ~40ms)
        if duration_ms > 0:
            dur_diff = abs(duration_ms - target_dur)
            score_dur = max(0.0, 1.0 - (dur_diff / 40.0))
        else:
            score_dur = 0.7

        # Composite weighted score: Frequency and Cadence are primary identifiers
        if interval_s > 0:
            composite_score = (score_freq * 0.50) + (score_interval * 0.35) + (score_dur * 0.15)
        else:
            composite_score = (score_freq * 0.75) + (score_dur * 0.25)

        if composite_score > highest_score:
            highest_score = composite_score
            best_match = BeepMatch(
                device_class=row["device_class"],
                brand=row["brand"],
                meaning=row["meaning"],
                severity=row["severity"],
                action=row["action"],
                source_url=row["source_url"],
                confidence=min(composite_score, 0.99),
                expected_interval_s=target_interval,
                expected_freq_hz=target_freq,
                expected_duration_ms=target_dur
            )

    return best_match
