"""
Server-Sent Events (SSE) Push Transport
Delivers real-time server-initiated proactive notifications to connected simulator clients.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Set, AsyncGenerator

logger = logging.getLogger("genius.proactive.sse")


class SSEEventBroadcaster:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(q)
        logger.info(f"SSE client connected. Total subscribers: {len(self._subscribers)}")
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)
        logger.info(f"SSE client disconnected. Total subscribers: {len(self._subscribers)}")

    async def broadcast(self, event_data: Dict[str, Any]):
        """Broadcasts an event formatted as SSE data frame."""
        if not self._subscribers:
            logger.info("No active SSE subscribers to receive event.")
            return

        payload = f"data: {json.dumps(event_data)}\n\n"
        dead_queues = set()
        for q in list(self._subscribers):
            try:
                await q.put(payload)
            except Exception as e:
                logger.warning(f"Error publishing to SSE subscriber queue: {e}")
                dead_queues.add(q)
        for dead in dead_queues:
            self._subscribers.discard(dead)

    async def stream_for_request(self, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
        """Async generator producing SSE stream with keep-alive heartbeats."""
        try:
            # Initial connection handshake
            handshake = {
                "type": "genius.connected",
                "message": "GENIUS Proactive SSE Channel Active (Spec 2025-11-25)",
                "timestamp": "now"
            }
            yield f"data: {json.dumps(handshake)}\n\n"

            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield data
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat comment
                    yield ": ping\n\n"
        finally:
            self.unsubscribe(queue)


# Singleton broadcaster
SSE_BROADCASTER = SSEEventBroadcaster()
