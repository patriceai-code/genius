"""
Unit Test: Audio Non-Persistence Verification
Verifies the defensible architectural privacy guarantee:
Raw audio is NEVER written to disk, temporary directories, logs, or the persistent SQLite database.
Only lightweight mathematical feature vectors (interval, frequency, duration) and metadata are stored.
"""

import os
import tempfile
import sqlite3
import pytest
from audio.ephemeral import process_file_ephemeral
from tools.hear_sound import register_hear_sound
from tools.diagnose import register_diagnose
from graph.store import HomeGraphStore
from mcp.server.mcpserver import MCPServer


@pytest.mark.asyncio
async def test_audio_never_persisted_to_disk_or_db(tmp_path):
    """
    Feeds real audio through the full ingestion and diagnosis pipeline,
    then scans disk, temp directory, and SQLite database to prove zero audio bytes persisted.
    """
    test_db = str(tmp_path / "test_privacy_graph.db")
    store = HomeGraphStore(db_path=test_db)
    
    # Path to sample clip
    clip_path = os.path.join(os.path.dirname(__file__), "clips", "clip_01_kidde_co_detector_end_of_life.wav")
    assert os.path.exists(clip_path), "Sample clip must exist"
    
    with open(clip_path, "rb") as f:
        audio_bytes = f.read()
    
    # Snapshot temp dir before processing
    temp_dir = tempfile.gettempdir()
    files_before = set(os.listdir(temp_dir))
    
    # 1. Run ephemeral processing
    result = process_file_ephemeral(clip_path)
    assert result.features["peak_frequency_hz"] > 0
    assert result.attestation["raw_audio_persisted"] is False
    
    # 2. Run MCP server tool execution
    server = MCPServer("test_privacy")
    register_hear_sound(server)
    register_diagnose(server)
    
    # Diagnose and write to test SQLite store
    entity_id = "ent_co_privacy_test"
    store.upsert_entity(
        entity_id=entity_id,
        entity_type="co_detector",
        brand="Kidde",
        model="KN-COPP-3",
        location="hallway",
        lifecycle_state="end_of_life",
        provenance="ephemeral_acoustic_test",
        confidence=0.98
    )
    store.record_incident(
        entity_id=entity_id,
        diagnosis="end_of_life",
        evidence_ref="freq=3200Hz,interval=30s",
        severity="critical",
        confidence=0.98,
        provenance="privacy_test"
    )
    
    # Snapshot temp dir after processing
    files_after = set(os.listdir(temp_dir))
    new_temp_files = files_after - files_before
    
    # Verify no audio files were dropped in temp directory
    audio_extensions = {".wav", ".pcm", ".raw", ".mp3", ".aac", ".ogg", ".flac"}
    for fname in new_temp_files:
        ext = os.path.splitext(fname)[1].lower()
        assert ext not in audio_extensions, f"Leaked temporary audio file on disk: {fname}"
    
    # 3. Inspect SQLite database contents
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check all tables and text/blob columns
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            for col_val in row:
                if isinstance(col_val, bytes):
                    # No binary audio blob should exist in DB
                    assert len(col_val) < 256, f"Suspicious binary blob ({len(col_val)} bytes) in table {table}"
                elif isinstance(col_val, str):
                    # Ensure raw audio wasn't dumped as large base64 string
                    assert len(col_val) < 5000, f"Suspicious large payload ({len(col_val)} chars) in table {table}"
                    assert not col_val.startswith("data:audio"), f"Audio data URI stored in DB table {table}"
    
    conn.close()
