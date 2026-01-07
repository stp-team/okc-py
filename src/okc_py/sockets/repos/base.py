"""Base WebSocket client for OKC real-time updates.

This module provides a low-level WebSocket connection handler that:
- Manages connection lifecycle (connect/disconnect)
- Handles authentication via cookies/session
- Implements Engine.IO protocol (ping/pong, packet parsing)
- Provides raw message interface (subclasses handle message parsing)

Subclasses should implement service-specific message parsing and event handling.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from aiohttp import WSMessage, WSMsgType

from okc_py.client import Client

logger = logging.getLogger(__name__)


class BaseWS(ABC):
    """Low-level WebSocket connection handler for OKC services.

    This class handles ONLY:
    - Connection management
    - Authentication (cookies, session ID)
    - Engine.IO protocol (ping/pong, packet parsing/sending)
    - Raw message loop

    Subclasses MUST:
    - Define service_url property
    - Implement on_message() for service-specific message handling
    - Handle Pydantic model conversion
    - Route events to registered handlers
    """

    def __init__(self, client: Client) -> None:
        """Initialize the WebSocket client.

        Args:
            client: Authenticated OKC API client
        """
        self.client = client
        self._ws: Any = None
        self._listen_task: asyncio.Task | None = None
        self._handlers: dict[str, list[Callable]] = {}

    # Abstract properties that subclasses must define
    @property
    @abstractmethod
    def service_url(self) -> str:
        """Get the WebSocket service URL/namespace.

        Subclasses must implement this to return their service-specific URL.

        Example:
            return "/ts-line-genesys-okcdb-ws"
        """
        raise NotImplementedError

    # URL and Authentication
    @property
    def base_url(self) -> str:
        """Get base URL for WebSocket connection."""
        return self.client.settings.BASE_URL.rstrip("/")

    def _get_websocket_url(self) -> str:
        """Build WebSocket URL for connection.

        Returns:
            Complete WebSocket URL with namespace and Engine.IO params
        """
        base = self.base_url.replace("/yii", "").replace("https://", "wss://")
        return f"{base}{self.service_url}/?EIO=4&transport=websocket"

    def _get_auth_cookies(self) -> str:
        """Get authentication cookies for WebSocket connection.

        Returns:
            Cookie header string for WebSocket authentication
        """
        return self.client.get_cookies()

    def _get_session_id(self) -> str | None:
        """Get PHPSESSID from cookies for WebSocket authorization.

        Returns:
            Session ID string or None if not found
        """
        session = self.client.get_session()
        if not session:
            return None
        for cookie in session.cookie_jar:
            if cookie.key == "PHPSESSID":
                return cookie.value
        return None

    # Engine.IO Protocol (Low-level)
    def _parse_engineio_packet(self, message: str) -> tuple[int, str, Any] | None:
        """Parse Engine.IO packet.

        Format: <packet_type>/<namespace>,<data>

        Engine.IO packet types:
        0 - open
        1 - close
        2 - ping
        3 - pong
        4 - message
        5 - upgrade
        6 - noop

        Args:
            message: Raw message string from WebSocket

        Returns:
            Tuple of (packet_type, namespace, data) or None if parse fails
        """
        try:
            if not message:
                return None

            packet_type = int(message[0])
            rest = message[1:]

            namespace = ""
            data = None

            if "/" in rest:
                parts = rest.split(",", 1)
                namespace_part = parts[0]
                if namespace_part.startswith("/"):
                    namespace = namespace_part
                if len(parts) > 1:
                    data = parts[1]
            else:
                data = rest if rest else None

            if data:
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            return packet_type, namespace, data
        except (ValueError, IndexError):
            return None

    async def _send_engineio_packet(
        self, packet_type: int, data: Any = None, namespace: str = ""
    ) -> None:
        """Send Engine.IO packet.

        Args:
            packet_type: Engine.IO packet type (0-6)
            data: Data payload to send
            namespace: Namespace for the packet

        Raises:
            RuntimeError: If WebSocket is not connected
        """
        if not self._ws:
            raise RuntimeError("WebSocket not connected")

        packet = str(packet_type)
        if namespace:
            packet += namespace
        if data is not None:
            packet += "," + (
                json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            )

        logger.debug(f"[WS] Sending packet: {packet}")
        await self._ws.send_str(packet)

    # Connection Management (Internal)
    async def _connect_websocket(self, ws_url: str) -> None:
        """Establish WebSocket connection.

        Args:
            ws_url: WebSocket URL to connect to

        Raises:
            RuntimeError: If connection fails or session not initialized
        """
        session = self.client.get_session()
        if not session:
            raise RuntimeError("Client session not initialized")

        self._ws = await session.ws_connect(
            ws_url,
            headers={
                "User-Agent": "okc-py-client",
                "Cookie": self._get_auth_cookies(),
                "Origin": self.base_url,
            },
        )

        msg: WSMessage = await self._ws.receive()
        logger.debug(f"[WS] Engine.IO open: {msg.type} = {msg.data}")

        if msg.type == WSMsgType.CLOSED:
            raise RuntimeError("WebSocket closed after connect")
        elif msg.type == WSMsgType.ERROR:
            raise RuntimeError(f"WebSocket error: {msg.data}")

    async def _send_connect_packet(self) -> None:
        """Send Socket.IO connect packet."""
        connect_packet = f"40{self.service_url},"
        logger.debug(f"[WS] Sending Socket.IO connect: {connect_packet}")
        await self._ws.send_str(connect_packet)

    async def _handle_connect_response(self) -> None:
        """Handle response to Socket.IO connect packet.

        Raises:
            RuntimeError: If connection closed or error occurred
        """
        msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
        logger.debug(f"[WS] First message: {msg.type} = {msg.data}")

        if msg.type == WSMsgType.TEXT and msg.data.startswith("40"):
            json_part = msg.data.split(",", 1)[1] if "," in msg.data else "{}"
            sid_data = json.loads(json_part)
            if "sid" in sid_data:
                logger.info(f"[WS] Session ID: {sid_data['sid']}")
        elif msg.type == WSMsgType.CLOSED:
            raise RuntimeError("WebSocket closed after connect packet")
        elif msg.type == WSMsgType.ERROR:
            raise RuntimeError(f"WebSocket error: {msg.data}")

    async def _handle_second_message(self) -> None:
        """Handle second message from server.

        Raises:
            RuntimeError: If connection closed or error occurred
        """
        msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
        logger.debug(f"[WS] Second message: {msg.type} = {msg.data}")

        if msg.type == WSMsgType.CLOSED:
            raise RuntimeError("WebSocket closed after session ID")
        elif msg.type == WSMsgType.ERROR:
            raise RuntimeError(f"WebSocket error: {msg.data}")

    async def _send_authentication(self) -> None:
        """Send authentication packet with session ID.

        Raises:
            RuntimeError: If WebSocket closed before sending auth
        """
        session_id = self._get_session_id()
        if not session_id:
            return

        if self._ws.closed:
            raise RuntimeError("WebSocket closed before auth send")

        auth_packet = f'42{self.service_url},["id","{session_id}"]'
        logger.debug(f"[WS] Sending auth: {auth_packet}")
        await self._ws.send_str(auth_packet)
        logger.info(f"[WS] Sent session ID: {session_id}")

    async def _finalize_connection(self) -> None:
        """Finalize WebSocket connection and start listening."""
        msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
        logger.debug(f"[WS] Third message (authData): {msg.type} = {msg.data}")

        self._listen_task = asyncio.create_task(self._listen_messages())
        logger.info("[WS] Connected successfully")

    # Message Loop
    async def _listen_messages(self) -> None:
        """Listen for WebSocket messages and route to subclass handler."""
        try:
            async for msg in self._ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_raw_message(msg.data)
                elif msg.type == WSMsgType.CLOSED:
                    logger.warning(
                        f"[WS] WebSocket closed by server. "
                        f"Code: {msg.data if msg.data else 'N/A'}"
                    )
                    break
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"[WS] WebSocket error: {msg.data}")
                    break
                elif msg.type == WSMsgType.CLOSING:
                    logger.warning("[WS] WebSocket closing...")
                    break
            logger.info("[WS] Listen loop ended")
        except asyncio.CancelledError:
            logger.info("[WS] Message listening stopped")
        except Exception as e:
            logger.error(f"[WS] Error listening: {e}", exc_info=True)

    async def _handle_raw_message(self, raw_message: str) -> None:
        """Handle raw WebSocket message.

        This method handles low-level protocol (ping/pong) and delegates
        service-specific messages to subclass via on_message().

        Args:
            raw_message: Raw message string from WebSocket
        """
        # Handle Engine.IO ping (respond with pong)
        if raw_message == "2":
            logger.debug("[WS] Ping received, sending pong")
            await self._send_engineio_packet(3)
            return

        # Parse Engine.IO packet
        parsed = self._parse_engineio_packet(raw_message)
        if not parsed:
            return

        packet_type, namespace, data = parsed

        # Packet type 4 = message, delegate to subclass
        if packet_type == 4:
            await self.on_message(data)

    # Abstract method for subclasses
    @abstractmethod
    async def on_message(self, data: Any) -> None:
        """Handle service-specific message data.

        Subclasses must implement this to:
        - Parse service-specific message format
        - Convert to Pydantic models if applicable
        - Route events to registered handlers via self._emit_event()

        Args:
            data: Parsed message data (from Engine.IO packet type 4)
        """
        raise NotImplementedError

    # Event handling for subclasses
    def _emit_event(self, event: str, event_data: Any) -> None:
        """Emit event to all registered handlers.

        Subclasses should call this to emit events after parsing messages.

        Args:
            event: Event name
            event_data: Event data to pass to handlers
        """
        if event not in self._handlers:
            return

        for handler in self._handlers[event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event_data))
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"[WS] Handler error for {event}: {e}", exc_info=True)

    # Public API
    async def connect(self) -> None:
        """Connect to WebSocket for real-time updates.

        Engine.IO protocol:
        1. Client sends: 40/<namespace>,
        2. Server responds: 40/<namespace>,{"sid":"..."}
        3. Server responds: 42/<namespace>,["connected"]
        4. Client sends: 42/<namespace>,["id","PHPSESSID"]
        5. Respond to ping (2) with pong (3)
        """
        if self._ws and not self._ws.closed:
            logger.warning("[WS] Already connected")
            return

        ws_url = self._get_websocket_url()
        logger.info(f"[WS] Connecting to: {ws_url}")

        try:
            await self._connect_websocket(ws_url)
            await self._send_connect_packet()
            await self._handle_connect_response()
            await self._handle_second_message()
            await self._send_authentication()
            await self._finalize_connection()
        except Exception as e:
            logger.error(f"[WS] Connection error: {e}")
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._ws and not self._ws.closed:
            await self._ws.close()
            logger.info("[WS] Disconnected")
        self._ws = None

    def on(self, event: str, handler: Callable) -> None:
        """Register handler for specific WebSocket event.

        Args:
            event: Event name (e.g., 'rawData', 'rawIncidents', 'breakUpdate')
            handler: Handler function receiving event data
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    async def emit(self, event: str, data: dict[str, Any] | list | None = None) -> None:
        """Send event through WebSocket.

        Args:
            event: Event name
            data: Data payload to send

        Raises:
            RuntimeError: If WebSocket is not connected
        """
        if not self._ws or self._ws.closed:
            raise RuntimeError("WebSocket not connected")

        packet_data: list[Any] = [event]
        if data is not None:
            packet_data.append(data)

        await self._send_engineio_packet(4, packet_data, namespace=self.service_url)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._ws is not None and not self._ws.closed

    # Context managers
    async def __aenter__(self):
        """Context manager for auto-connect."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager for auto-disconnect."""
        await self.disconnect()
