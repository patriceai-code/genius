"""
Smart Home API Push Transport (Deferred Stub)
Reference: ADR 002 - Smart Home API Deferral (Alexa.ProactiveNotificationSource)

Status: Deferred.
Rationale: Requires rigid ChangeReport schemas, secondary OAuth account linking,
and non-MCP infrastructure. Kept as architectural documentation.
"""

import logging

logger = logging.getLogger("genius.proactive.smart_home")


class SmartHomeNotificationSourceStub:
    """
    Stub documenting why classic Alexa.ProactiveNotificationSource was deferred in favor
    of the modern self-hosted MCP Streamable HTTP + SSE design.
    """
    def __init__(self):
        self.status = "deferred"
        self.reason = "ADR 002: Avoid OAuth account linking; maintain architectural privacy by construction."
