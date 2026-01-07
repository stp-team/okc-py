"""Breaks WebSocket API for OKC real-time updates."""

import logging
from typing import Any

from okc_py.client import Client
from okc_py.sockets.repos.base import BaseWS

logger = logging.getLogger(__name__)


class BreaksWSClient(BaseWS):
    """WebSocket client for breaks updates.

    Real-time events for break notifications and updates.

    Example:
        ```python
        breaks = BreaksWSClient(client)
        await breaks.connect()

        # Register handler for break events
        breaks.on("breakUpdate", lambda data: print(f"Break: {data}"))
        ```
    """

    def __init__(self, client: Client) -> None:
        """Initialize Breaks WebSocket client.

        Args:
            client: Authenticated OKC API client
        """
        super().__init__(client)

    @property
    def service_url(self) -> str:
        """Get the WebSocket service URL for breaks."""
        return "/break-nck-ntp-ws"

    async def on_message(self, data: Any) -> None:
        """Handle Breaks-specific event messages.

        Break events include notifications about operators going on/off breaks,
        break duration updates, and break schedule changes.

        This method:
        1. Parses the event format: [event_name, event_data]
        2. Logs the event appropriately
        3. Emits to registered handlers via self._emit_event()

        Args:
            data: Parsed event data (typically [event_name, event_data])
        """
        if not isinstance(data, list) or len(data) < 1:
            return

        event = data[0]
        event_data = data[1] if len(data) > 1 else None

        # Log break-specific events
        if event_data and isinstance(event_data, dict):
            keys = list(event_data.keys())[:5]
            logger.debug(f"[Breaks] Event: {event}, keys: {keys}")
        else:
            logger.debug(f"[Breaks] Event: {event}, data: {event_data}")

        # Emit to registered handlers
        self._emit_event(event, event_data)
