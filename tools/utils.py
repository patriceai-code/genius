"""
Utility helpers for Bedrock LLM outputs and schema parsing.
"""

import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("genius.tools.utils")


def parse_json_from_llm(text: str) -> Dict[str, Any]:
    """
    Robustly extracts and parses a JSON object from LLM response text.
    Handles:
    - Markdown fenced code blocks (```json ... ```)
    - Preamble and postamble commentary
    - Raw JSON dict strings
    """
    if not text:
        raise ValueError("Empty response text from LLM")

    cleaned = text.strip()

    # 1. Try markdown code block extraction
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, cleaned)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 2. Try matching the outermost curly braces { ... }
    brace_pattern = r"(\{[\s\S]*\})"
    match_braces = re.search(brace_pattern, cleaned)
    if match_braces:
        candidate = match_braces.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 3. Direct JSON parse
    return json.loads(cleaned)
