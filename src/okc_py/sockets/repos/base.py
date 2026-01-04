"""Base WebSocket client for OKC real-time APIs."""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from aiohttp import ClientSession, WSMessage, WSMsgType

from okc_py.client import Client

logger = logging.getLogger(__name__)


class BaseWebSocketClient(ABC):
    """Base class for WebSocket connections to OKC.

    Implements Engine.IO/WebSocket protocol for real-time updates.
    Subclasses should define their namespace and auth logic.
    """

    def __init__(self, client: Client, namespace: str):
        """Initialize the WebSocket client.

        Args:
            client: Authenticated OKC API client
            namespace: WebSocket namespace (e.g., "/ts-line-genesys-okcdb-ws")
        """
        self.client = client
        self._namespace = namespace
        self._ws: ClientSession.ws_connect | None = None
        self._message_handlers: dict[str, list[Callable]] = {}
        self._listen_task: asyncio.Task | None = None

    @property
    def base_url(self) -> str:
        """Get base URL for WebSocket connection."""
        return self.client.settings.BASE_URL.rstrip("/")

    @abstractmethod
    async def _get_auth_cookies(self) -> str:
        """Get authentication cookies for WebSocket connection.

        Returns:
            Cookie header string for WebSocket authentication
        """
        pass

    async def _get_websocket_url(self) -> str:
        """Form WebSocket URL for connection.

        Returns:
            Complete WebSocket URL with namespace and Engine.IO params
        """
        base = self.base_url.replace("/yii", "").replace("https://", "wss://")
        return f"{base}{self._namespace}/?EIO=4&transport=websocket"

    async def _parse_engineio_packet(self, message: str) -> tuple[int, str, Any] | None:
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
                except json.JSONDecodeError as e:
                    logger.debug(
                        f"[WS] JSON parse error: {e}, data length: {len(data) if data else 0}"
                    )
                    pass

            return packet_type, namespace, data
        except (ValueError, IndexError) as e:
            logger.debug(f"[WS] Failed to parse packet: {e}, message: {message[:100]}")
            return None

    async def _send_engineio_packet(
        self, packet_type: int, data: Any = None, namespace: str = ""
    ) -> None:
        """Send Engine.IO packet.

        Args:
            packet_type: Engine.IO packet type (0-6)
            data: Data payload to send
            namespace: Namespace for the packet
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

    async def _get_session_id(self) -> str | None:
        """Get PHPSESSID from cookies for WebSocket authorization.

        Returns:
            Session ID string or None if not found
        """
        if not self.client._session:
            return None
        for cookie in self.client._session.cookie_jar:
            if cookie.key == "PHPSESSID":
                return cookie.value
        return None

    async def _listen_messages(self) -> None:
        """Listen for WebSocket messages and call registered handlers."""
        try:
            async for msg in self._ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_message(msg.data)
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

    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket message.

        Args:
            message: Raw message string
        """
        if len(message) > 200:
            logger.debug(f"[WS] Received ({len(message)} chars): {message[:100]}...")
        else:
            logger.debug(f"[WS] Received: {message}")

        if message == "2":
            logger.debug("[WS] Ping received, sending pong")
            await self._send_engineio_packet(3)
            return

        try:
            parsed = await self._parse_engineio_packet(message)
            if not parsed:
                return

            packet_type, namespace, data = parsed

            if packet_type == 4 and data:
                if isinstance(data, list) and len(data) >= 1:
                    event = data[0]
                    event_data = data[1] if len(data) > 1 else None

                    if event_data and isinstance(event_data, dict):
                        logger.info(
                            f"[WS] Event: {event}, keys: {list(event_data.keys())[:10]}"
                        )
                    else:
                        logger.info(f"[WS] Event: {event}, data: {event_data}")

                    if event in self._message_handlers:
                        for handler in self._message_handlers[event]:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(event_data)
                                else:
                                    handler(event_data)
                            except Exception as e:
                                logger.error(
                                    f"[WS] Handler error for {event}: {e}",
                                    exc_info=True,
                                )
        except Exception as e:
            logger.error(
                f"[WS] Error handling message: {e}, message: {message[:200]}",
                exc_info=True,
            )

    async def connect(
        self,
        message_handler: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        """Connect to WebSocket for real-time updates.

        Engine.IO protocol:
        1. Client sends: 40/<namespace>,
        2. Server responds: 40/<namespace>,{"sid":"..."}
        3. Server responds: 42/<namespace>,["connected"]
        4. Client sends: 42/<namespace>,["id","PHPSESSID"]
        5. Respond to ping (2) with pong (3)

        Args:
            message_handler: Optional handler for incoming messages.
                Receives (event, data) as arguments.
        """
        if self._ws and not self._ws.closed:
            logger.warning("[WS] Already connected")
            return

        ws_url = await self._get_websocket_url()
        logger.info(f"[WS] Connecting to: {ws_url}")

        if message_handler:
            self.on("message", lambda d: message_handler("message", d))

        try:
            self._ws = await self.client._session.ws_connect(
                ws_url,
                headers={
                    "User-Agent": "okc-py-client",
                    "Cookie": await self._get_auth_cookies(),
                    "Origin": self.base_url,
                },
            )

            msg: WSMessage = await self._ws.receive()
            logger.debug(f"[WS] Engine.IO open: {msg.type} = {msg.data}")

            if msg.type == WSMsgType.CLOSED:
                raise RuntimeError("WebSocket closed after connect")
            elif msg.type == WSMsgType.ERROR:
                raise RuntimeError(f"WebSocket error: {msg.data}")

            connect_packet = f"40{self._namespace},"
            logger.debug(f"[WS] Sending Socket.IO connect: {connect_packet}")
            await self._ws.send_str(connect_packet)

            msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
            logger.debug(f"[WS] First message: {msg.type} = {msg.data}")

            if msg.type == WSMsgType.TEXT:
                if msg.data.startswith("40"):
                    json_part = msg.data.split(",", 1)[1] if "," in msg.data else "{}"
                    sid_data = json.loads(json_part)
                    if "sid" in sid_data:
                        logger.info(f"[WS] Session ID: {sid_data['sid']}")
            elif msg.type == WSMsgType.CLOSED:
                raise RuntimeError("WebSocket closed after connect packet")
            elif msg.type == WSMsgType.ERROR:
                raise RuntimeError(f"WebSocket error: {msg.data}")

            msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
            logger.debug(f"[WS] Second message: {msg.type} = {msg.data}")

            if msg.type == WSMsgType.CLOSED:
                raise RuntimeError("WebSocket closed after session ID")
            elif msg.type == WSMsgType.ERROR:
                raise RuntimeError(f"WebSocket error: {msg.data}")

            session_id = await self._get_session_id()
            if session_id:
                if self._ws.closed:
                    raise RuntimeError("WebSocket closed before auth send")
                auth_packet = f'42{self._namespace},["id","{session_id}"]'
                logger.debug(f"[WS] Sending auth: {auth_packet}")
                await self._ws.send_str(auth_packet)
                logger.info(f"[WS] Sent session ID: {session_id}")

            msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
            logger.debug(f"[WS] Third message (authData): {msg.type} = {msg.data}")

            self._listen_task = asyncio.create_task(self._listen_messages())
            logger.info("[WS] Connected successfully")

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
            event: Event name (e.g., 'rawData', 'rawIncidents')
            handler: Handler function receiving event data
        """
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)

    async def emit(self, event: str, data: dict[str, Any] | list | None = None) -> None:
        """Send event through WebSocket.

        Args:
            event: Event name
            data: Data payload to send
        """
        if not self._ws or self._ws.closed:
            raise RuntimeError("WebSocket not connected")

        packet_data = [event]
        if data is not None:
            packet_data.append(data)

        await self._send_engineio_packet(4, packet_data, namespace=self._namespace)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._ws is not None and not self._ws.closed

    async def __aenter__(self):
        """Context manager for auto-connect."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager for auto-disconnect."""
        await self.disconnect()
