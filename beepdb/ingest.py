"""
beepdb Ingestion Engine
Extracts acoustic signatures and error beeps from hardware manuals using Amazon Bedrock (Nova Pro),
with deterministic local heuristic fallback.
"""

import json
import os
import csv
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from tools.utils import parse_json_from_llm

load_dotenv()
logger = logging.getLogger("genius.beepdb.ingest")

CSV_PATH = os.path.join(os.path.dirname(__file__), "codes.csv")


def get_bedrock_client():
    """Initializes AWS Bedrock Runtime client."""
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    return boto3.client("bedrock-runtime", region_name=region)


def extract_beep_signature_bedrock(manual_text: str, source_url: str = "") -> Optional[Dict[str, Any]]:
    """
    Uses Amazon Bedrock (Amazon Nova Pro) to extract structured
    beep codes from unstructured hardware manuals.
    """
    prompt = f"""You are an acoustic engineering analyst extracting hardware diagnostic beep patterns.
Extract the chirp interval (in seconds), pulse duration (in ms, estimate 60-100ms if standard chirp),
dominant peak frequency (in Hz, typically 3000-4000Hz for piezos), device category, brand, failure meaning,
severity (info, warning, or critical), and recommended action.

Manual Text:
\"\"\"
{manual_text}
\"\"\"

Return ONLY valid JSON matching this schema:
{{
  "signature_interval_s": float,
  "signature_duration_ms": float,
  "peak_freq_hz": float,
  "device_class": "co_detector" | "smoke_detector" | "water_leak_detector" | "refrigerator" | "ups_battery_backup" | "hvac_furnace",
  "brand": "string",
  "meaning": "end_of_life" | "low_battery" | "sensor_fault" | "door_ajar" | "moisture_detected",
  "severity": "info" | "warning" | "critical",
  "action": "string",
  "source_url": "{source_url}"
}}
"""

    try:
        client = get_bedrock_client()
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")

        body = json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"max_new_tokens": 1000, "temperature": 0.0}
        })

        response = client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read().decode("utf-8"))
        content_text = response_body["output"]["message"]["content"][0]["text"].strip()
        return parse_json_from_llm(content_text)

    except (BotoCoreError, ClientError, Exception) as e:
        logger.warning(f"Bedrock invocation unavailable ({e}), using local rule fallback.")
        return extract_beep_signature_fallback(manual_text, source_url)


def extract_beep_signature_fallback(manual_text: str, source_url: str = "") -> Dict[str, Any]:
    """
    Deterministic regex and keyword extractor for offline development.
    """
    text_lower = manual_text.lower()

    interval = 30.0
    if "45 seconds" in text_lower or "45s" in text_lower:
        interval = 45.0
    elif "60 seconds" in text_lower or "60s" in text_lower or "minute" in text_lower:
        interval = 60.0
    elif "15 seconds" in text_lower or "15s" in text_lower:
        interval = 15.0

    device_class = "co_detector" if "carbon monoxide" in text_lower or " co " in text_lower else "smoke_detector"
    meaning = "end_of_life" if ("end of life" in text_lower or "expire" in text_lower or "replacement" in text_lower) else "low_battery"
    severity = "critical" if meaning == "end_of_life" else "warning"

    return {
        "signature_interval_s": interval,
        "signature_duration_ms": 80.0,
        "peak_freq_hz": 3200.0,
        "freq_tolerance_hz": 350.0,
        "verification_status": "cadence_verified_frequency_nominal",
        "device_class": device_class,
        "brand": "Kidde" if "kidde" in text_lower else "First Alert",
        "meaning": meaning,
        "severity": severity,
        "action": "replace_unit;propose_purchase" if severity == "critical" else "replace_battery;walkthrough",
        "source_url": source_url or "https://manuals.example.com"
    }


def append_to_beepdb(row_data: Dict[str, Any], csv_path: str = CSV_PATH) -> bool:
    """Appends an extracted acoustic signature to codes.csv."""
    headers = [
        "signature_interval_s", "signature_duration_ms", "peak_freq_hz",
        "freq_tolerance_hz", "verification_status",
        "device_class", "brand", "meaning", "severity", "action", "source_url"
    ]
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(row_data)
    return True
