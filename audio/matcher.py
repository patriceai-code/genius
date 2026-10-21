"""
beepdb Acoustic Matcher
Matches extracted sound features (cadence interval, peak frequency, pulse duration)
against the sourced beepdb database. Returns candidate device, severity, confidence,
verification status, and the canonical 3 AM diagnostic explanation.
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
        expected_duration_ms: float,
        verification_status: str = "cadence_verified_frequency_nominal"
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
        self.verification_status = verification_status

    def format_3am_speech(self, location: str = "hallway") -> str:
        """
        Generates calibrated 3 AM voice readout based on epistemic confidence:
        - >= 0.95: Direct factual assertion
        - 0.80 - 0.94: Hedged nearest-pattern probability ("most consistent with...")
        - < 0.80: Inquisitive clarifying follow-up
        """
        loc_phrase = f"in your {location}" if location else "in your home"
        device_title = f"{self.brand} {self.device_class.replace('_', ' ').title()}"
        class_desc = self.device_class.replace('_', ' ')

        # Tier 1: High Confidence (>= 0.95) - Definite assertion
        if self.confidence >= 0.95:
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

        # Tier 2: Moderate Confidence (0.80 - 0.94) - Hedged pattern consistency
        elif self.confidence >= 0.80:
            if self.meaning == "end_of_life":
                return (
                    f"This sound is most consistent with an end-of-life sensor alert, likely your {device_title} {loc_phrase}. "
                    f"I have staged a replacement proposal for your review."
                )
            elif self.meaning == "low_battery":
                return (
                    f"This sound is most consistent with a low battery alert, likely your {device_title} {loc_phrase}. "
                    f"The cadence matches a {int(self.expected_interval_s)}-second interval."
                )
            elif self.meaning == "door_ajar":
                return (
                    f"This alert pattern is most consistent with a door left ajar, possibly your {device_title}. "
                    f"Please check that the door is closed completely."
                )
            elif self.meaning == "on_battery_power":
                return (
                    f"This alert matches a battery-backup power transition, likely your {device_title} running on internal battery."
                )
            else:
                return (
                    f"This sound pattern is most consistent with your {device_title} {loc_phrase} indicating {self.meaning.replace('_', ' ')} "
                    f"({int(self.confidence * 100)}% pattern match)."
                )


        # Tier 3: Low Confidence (< 0.80) - Exploratory follow-up
        else:
            return (
                f"I detected an acoustic pattern near {int(self.expected_freq_hz)} Hertz with a {int(self.expected_interval_s)}-second interval. "
                f"It may be related to your {device_title} {loc_phrase}, but my confidence is low at {int(self.confidence * 100)} percent. "
                f"Could you verify if that {class_desc} is the one making the sound?"
            )


    def to_dict(self, location: str = "hallway") -> Dict[str, Any]:
        return {
            "device_class": self.device_class,
            "brand": self.brand,
            "meaning": self.meaning,
            "severity": self.severity,
            "action": self.action,
            "confidence": self.confidence,
            "verification_status": self.verification_status,
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
                "freq_tolerance_hz": float(r.get("freq_tolerance_hz", 350.0)),
                "verification_status": r.get("verification_status", "cadence_verified_frequency_nominal"),
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
    Uses calibrated frequency tolerance bands (±250-400Hz) and prioritizes digital cadence intervals.
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
        tol_freq = row.get("freq_tolerance_hz", 350.0)

        # 1. Cadence interval score (digital timer cadence)
        if interval_s > 0:
            interval_diff = abs(interval_s - target_interval)
            # Allow tight tolerance for interval (e.g. within 20% or 3s)
            score_interval = max(0.0, 1.0 - (interval_diff / max(target_interval * 0.20, 3.0)))
        else:
            score_interval = 0.5  # Neutral if single chirp captured

        # 2. Resonant peak frequency score (scaled by piezo/component tolerance window)
        freq_diff = abs(peak_freq_hz - target_freq)
        score_freq = max(0.0, 1.0 - (freq_diff / tol_freq))

        # 3. Pulse duration score (tolerance ~50ms)
        if duration_ms > 0:
            dur_diff = abs(duration_ms - target_dur)
            score_dur = max(0.0, 1.0 - (dur_diff / 50.0))
        else:
            score_dur = 0.7

        # Composite weighted score:
        # Cadence timing is primary (digital timer code), Frequency validates acoustic hardware family
        if interval_s > 0:
            composite_score = (score_interval * 0.55) + (score_freq * 0.35) + (score_dur * 0.10)
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
                expected_duration_ms=target_dur,
                verification_status=row.get("verification_status", "cadence_verified_frequency_nominal")
            )

    return best_match
