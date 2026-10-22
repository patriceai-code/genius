"""
beepdb — Open Database of Hardware Acoustic Signatures & Diagnostic Beep Codes
"""

from .core import (
    BeepSignature,
    load_database,
    search_signatures,
    match_beep,
    match_description,
)

__version__ = "0.2.0"
__all__ = [
    "BeepSignature",
    "load_database",
    "search_signatures",
    "match_beep",
    "match_description",
]
