"""API вебсокетов для отслеживания состояния перерывов."""

import asyncio
import logging
from typing import Any, Literal

from ...client import Client
from ...sockets.models import (
    AuthMessage,
    PageData,
    SimplePageData,
    UserBreaks,
)
from ...sockets.repos.base import BaseWS

logger = logging.getLogger(__name__)

BreakNamespace = Literal[
    "ntp_one",
    "ntp_two",
    "ntp_nck",
]

BREAK_NAMESPACES: dict[BreakNamespace, str] = {
    "ntp_one": "/ntp-one-break-ws",
    "ntp_two": "/ntp-two-break-ws",
    "ntp_nck": "/break-nck-ntp-ws",
}


class BreaksWSClient(BaseWS):
    """WebSocket client for breaks updates.

    Real-time events for break notifications and updates.

    Events:
    - authMessage: Authorization confirmation with user info
      Example: {"userName": "...", "isSuperUser": false}
    - userBreaks: User's breaks count per line
      Example: {"line5": 0, "line10": 0, "line15": 3}
    - pageData: Full page data with lines and queue tables

    Connection flow:
    1. Send Socket.IO connect packet
    2. Receive session ID (sid)
    3. Send auth packet with session ID
    4. Receive authMessage and userBreaks (confirmation)
    5. Receive pageData updates

    Example:
        ```python
        breaks = BreaksWSClient(client, "ntp-nck")
        await breaks.connect()

        # Register handlers
        breaks.on("authMessage", lambda data: print(f"User: {data.user_name}"))
        breaks.on("userBreaks", lambda data: print(f"Total: {data.total}"))
        breaks.on("pageData", lambda data: print(f"Lines: {data.lines}"))
        ```
    """

    def __init__(self, client: Client, namespace: BreakNamespace = "ntp-nck") -> None:
        """Initialize Breaks WebSocket client.

        Args:
            client: Authenticated OKC API client
            namespace: Break namespace (ntp-one, ntp-two, ntp-nck)
        """
        self._namespace = namespace
        super().__init__(client)

    @property
    def service_url(self) -> str:
        """Get the WebSocket service URL for this break namespace."""
        return BREAK_NAMESPACES.get(self._namespace, BREAK_NAMESPACES["ntp_nck"])

    async def connect(self) -> None:
        """Connect to WebSocket for breaks updates.

        Breaks socket has a different flow than other sockets:
        1. Client sends: 40/break-nck-ntp-ws,
        2. Server responds: 40/break-nck-ntp-ws,{"sid":"..."}
        3. Client sends: 42/break-nck-ntp-ws,["id","PHPSESSID"]
        4. Server sends: 42/break-nck-ntp-ws,["userBreaks",{...}]
        5. Server sends: 42/break-nck-ntp-ws,["authMessage",{...}]
        6. Server sends: 42/break-nck-ntp-ws,["pageData",{...}] (repeated)
        7. Respond to ping (2) with pong (3)

        Note: Unlike lines socket, breaks socket does NOT send ["connected"]
        after the Socket.IO connect acknowledgment.
        """
        if self._ws and not self._ws.closed:
            logger.warning("[WS] Already connected")
            return

        ws_url = self._get_websocket_url()
        logger.info(f"[Breaks] Connecting to: {ws_url}")

        try:
            # Step 1: Connect to WebSocket (gets Engine.IO open)
            await self._connect_websocket(ws_url)

            # Step 2: Send Socket.IO connect packet
            await self._send_connect_packet()

            # Step 3: Handle Socket.IO connect response (with sid)
            await self._handle_connect_response()

            # Step 4: Send auth packet immediately (no "connected" message from breaks socket)
            await self._send_authentication()

            # Step 5: Start listening for events
            self._listen_task = asyncio.create_task(self._listen_messages())
            logger.info("[Breaks] Connected successfully")

        except Exception as e:
            logger.error(f"[Breaks] Connection error: {e}")
            await self.disconnect()
            raise

    async def on_message(self, data: Any) -> None:
        """Handle Breaks-specific event messages.

        Break events:
        - authMessage: User authorization confirmation
        - userBreaks: User's breaks count per line
        - pageData: Full page data with lines status and operator queue

        This method:
        1. Parses the event format: [event_name, event_data]
        2. Validates data through Pydantic models
        3. Logs the event appropriately
        4. Emits to registered handlers via self._emit_event()

        Args:
            data: Parsed event data (typically [event_name, event_data])
        """
        if not isinstance(data, list) or len(data) < 1:
            return

        event = data[0]
        event_data = data[1] if len(data) > 1 else None

        # Process events and validate through Pydantic
        if event == "authMessage" and event_data and isinstance(event_data, dict):
            try:
                auth_msg = AuthMessage(**event_data)
                logger.info(
                    f"[Breaks:{self._namespace}] Authorized as: {auth_msg.user_name}"
                )
                self._emit_event(event, auth_msg)
                return
            except Exception as e:
                logger.warning(
                    f"[Breaks:{self._namespace}] Failed to validate AuthMessage: {e}"
                )
        elif event == "userBreaks" and event_data and isinstance(event_data, dict):
            try:
                user_breaks = UserBreaks(**event_data)
                logger.info(
                    f"[Breaks:{self._namespace}] User breaks: {user_breaks.total} total"
                )
                self._emit_event(event, user_breaks)
                return
            except Exception as e:
                logger.warning(
                    f"[Breaks:{self._namespace}] Failed to validate UserBreaks: {e}"
                )
        elif event == "pageData" and event_data and isinstance(event_data, dict):
            try:
                # Use different models based on namespace
                # ntp_one and ntp_two use simpler format without discharge data
                # ntp_nck uses full format with discharge data
                if self._namespace in ("ntp_one", "ntp_two"):
                    page_data = SimplePageData(**event_data)
                else:
                    page_data = PageData(**event_data)
                logger.debug(
                    f"[Breaks:{self._namespace}] Page data: {len(page_data.lines)} lines"
                )
                self._emit_event(event, page_data)
                return
            except Exception as e:
                logger.warning(
                    f"[Breaks:{self._namespace}] Failed to validate PageData: {e}"
                )
        else:
            logger.debug(
                f"[Breaks:{self._namespace}] Event: {event}, data: {event_data}"
            )

        # Emit raw data to handlers (fallback)
        self._emit_event(event, event_data)
