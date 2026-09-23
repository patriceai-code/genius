"""
MCP Inbound Device Push Transport (Dormant Stub)
Reference: ADR 001 - Proactive Push Transport Strategy

Status: Dormant.
Context: Alexa+ Preview (as of September 2026) does not currently expose direct unsolicited
inbound notification sockets into Echo devices for third-party MCP servers.
This module maintains the spec-compliant push protocol stub that will activate seamlessly
the moment Amazon ships unsolicited device push to the Alexa+ developer toolkit.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("genius.proactive.mcp_push")


class MCPDevicePushTransport:
    def __init__(self):
        self.is_supported_by_preview = False

    async def push_to_alexa_device(self, device_id: str, event_payload: Dict[str, Any]) -> bool:
        """
        Dormant push implementation.
        Logs status and delegates to SSE simulator client.
        """
        if not self.is_supported_by_preview:
            logger.debug(
                "Direct MCP device push not yet available in Alexa+ Preview. "
                "Event routed through SSE transport to simulator client."
            )
            return False

        # Future implementation once Amazon enables inbound MCP push
        return True


MCP_PUSH_TRANSPORT = MCPDevicePushTransport()
