"""
Amazon Polly Neural TTS Integration for GENIUS Simulator & Audio Responses.
Supports neural voice synthesis (e.g. Joanna) with streaming audio output.
"""

import os
import io
import logging
from typing import Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger("genius.audio.tts")


def synthesize_speech(text: str, voice_id: str = "Joanna", engine: str = "neural") -> Optional[bytes]:
    """
    Synthesizes speech using Amazon Polly Neural TTS.
    Returns MP3 audio bytes, or None if service unavailable.
    """
    if not text or not text.strip():
        return None
    try:
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        client = boto3.client("polly", region_name=region)
        response = client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine,
        )
        if "AudioStream" in response:
            return response["AudioStream"].read()
    except (BotoCoreError, ClientError) as e:
        logger.warning(f"Amazon Polly synthesis unavailable ({e}), client will use local Web Speech API fallback.")
    except Exception as ex:
        logger.warning(f"Unexpected Polly error: {ex}")
    return None
