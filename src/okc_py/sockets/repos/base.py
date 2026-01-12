import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from aiohttp import WSMessage, WSMsgType

from ...client import Client

logger = logging.getLogger(__name__)


class BaseWS(ABC):
    """Низкоуровневый обработчик WebSocket'ов.

    Этот класс обрабатывает только:
    - Подключение к сокету
    - Аутентификацию (cookies, session ID)
    - Engine.IO протокол (ping/pong, парсинг пакетов)
    - Петлю сообщений

    Подклассы должны:
    - Определять свойство service_url
    - Определить метод on_message() для специфичного сервису обработчика сообщений
    - Обрабатывать ответы Pydantic моделями
    """

    def __init__(self, client: Client) -> None:
        """Инициализация клиента.

        Args:
            client: Авторизованный клиент OKC
        """
        self.client = client
        self._ws: Any = None
        self._listen_task: asyncio.Task | None = None
        self._handlers: dict[str, list[Callable]] = {}

    @property
    @abstractmethod
    def service_url(self) -> str:
        """Получить URL/namespace WebSocket сервиса.

        Подклассы должны определить это свойство.

        Пример:
            return "/ts-line-genesys-okcdb-ws"
        """
        raise NotImplementedError

    # URL и авторизация
    @property
    def base_url(self) -> str:
        """Получить базовый URL для подключения к WebSocket."""
        return self.client.settings.BASE_URL.rstrip("/")

    def _get_websocket_url(self) -> str:
        """Построить WebSocket URL для подключения.

        Returns:
            Готовый WebSocket URL с namespace и параметрами Engine.IO
        """
        base = self.base_url.replace("/yii", "").replace("https://", "wss://")
        return f"{base}{self.service_url}/?EIO=4&transport=websocket"

    def _get_auth_cookies(self) -> str:
        """Получить авторизованные cookies для WebSocket connection.

        Returns:
            Строка заголовков cookie для авторизации в WebSocket
        """
        return self.client.get_cookies()

    def _get_session_id(self) -> str | None:
        """Получить PHPSESSID из cookies для авторизации.

        Returns:
            Строка Session ID или None если не найдено
        """
        session = self.client.get_session()
        if not session:
            return None
        for cookie in session.cookie_jar:
            if cookie.key == "PHPSESSID":
                return cookie.value
        return None

    # Обработка пакетов Engine.IO
    @staticmethod
    def _parse_packet(message: str) -> tuple[int, str, Any] | None:
        """Парсинг пакета Engine.IO.

        Формат: <packet_type>/<namespace>,<data>

        Типы пакетов:
        0 - open
        1 - close
        2 - ping
        3 - pong
        4 - message
        5 - upgrade
        6 - noop

        Args:
            message: Сырое сообщение из WebSocket

        Returns:
            Кортеж (packet_type, namespace, data) или None если парсинг пакета провалился
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

    async def _send_packet(
        self, packet_type: int, data: Any = None, namespace: str = ""
    ) -> None:
        """Отправить пакет Engine.IO.

        Args:
            packet_type: Тип пакета Engine.IO для отправки (0-6)
            data: Полезная нагрузка
            namespace: Namespace для пакета

        Raises:
            RuntimeError: Если WebSocket не подключен
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

    # Подключения (Internal)
    async def _connect_websocket(self, ws_url: str) -> None:
        """Установить WebSocket подключение.

        Args:
            ws_url: WebSocket URL для подключения

        Raises:
            RuntimeError: Если подключение провалено или сессия не инициализирована
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
        """Отправить Socket.IO пакет подключения."""
        connect_packet = f"40{self.service_url},"
        logger.debug(f"[WS] Sending Socket.IO connect: {connect_packet}")
        await self._ws.send_str(connect_packet)

    async def _handle_connect_response(self) -> None:
        """Обработать ответный пакет Socket.IO при подключении.

        Raises:
            RuntimeError: Если соединение закрыто или произошла ошибка
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
        """Обрабатывает второе сообщение от сервера.

        Raises:
            RuntimeError: Если соединение закрыто или произошла ошибка
        """
        msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
        logger.debug(f"[WS] Second message: {msg.type} = {msg.data}")

        if msg.type == WSMsgType.CLOSED:
            raise RuntimeError("WebSocket closed after session ID")
        elif msg.type == WSMsgType.ERROR:
            raise RuntimeError(f"WebSocket error: {msg.data}")

    async def _send_authentication(self) -> None:
        """Отправляет пакет авторизации с session ID.

        Raises:
            RuntimeError: Если WebSocket закрыт до отправки авторизации
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
        """Завершает подключение к WebSocket и начинает слушать сообщения."""
        msg = await asyncio.wait_for(self._ws.receive(), timeout=5.0)
        logger.debug(f"[WS] Third message (authData): {msg.type} = {msg.data}")

        self._listen_task = asyncio.create_task(self._listen_messages())
        logger.info("[WS] Connected successfully")

    # Цикл сообщений
    async def _listen_messages(self) -> None:
        """Слушает сообщения WebSocket и роутит в подклассовые обработчики."""
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
        """Обработать сырое сообщение WebSocket.

        Этот метод обрабатывает низкоуровневые сообщения и
        делегирует специфичные сервисам сообщения в их подклассы
        через on_message().

        Args:
            raw_message: Строка с сырым сообщением из WebSocket
        """
        # Обрабатываем пинг Engine.IO
        if raw_message == "2":
            logger.debug("[WS] Ping received, sending pong")
            await self._send_packet(3)
            return

        # Парсим пакет Engine.IO
        parsed = self._parse_packet(raw_message)
        if not parsed:
            return

        packet_type, namespace, data = parsed

        # Пакет с типом 4 = сообщение, делегируемое подклассам
        if packet_type == 4:
            await self.on_message(data)

    # Абстрактный метод для подклассов
    @abstractmethod
    async def on_message(self, data: Any) -> None:
        """Обрабатывает специфичные сообщения сервисов.

        Сабклассы должны переопределить метод для:
        - Парсинга сообщений в специфичном формате
        - Конвертирования в Pydantic модели
        - Роутинга ивентов в зарегистрированные обработчики через self._emit_event()

        Args:
            data: Анализируемые данные сообщения (из Engine.IO с типом пакета - 4)
        """
        raise NotImplementedError

    # Обработчик ивентов для подклассов
    def _emit_event(self, event: str, event_data: Any) -> None:
        """Отправить событие всем зарегистрированным обработчикам.

        Подклассы должны вызывать этот метод после парсинга сообщений.

        Args:
            event: Название ивента
            event_data: Данные ивента для пуша в обработчики
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
        """Подключиться к WebSocket.

        Engine.IO протокол:
        1. Клиент отправляет: 40/<namespace>,
        2. Сервер отвечает: 40/<namespace>,{"sid":"..."}
        3. Клиент отправляет: 42/<namespace>,["id","PHPSESSID"]
        4. Сервер отвечает: 42/<namespace>,["authName",...] и сразу данные
        5. Отвечаем на пинг (2) - понг (3)
        """
        if self._ws and not self._ws.closed:
            logger.warning("[WS] Already connected")
            return

        ws_url = self._get_websocket_url()
        logger.info(f"[WS] Connecting to: {ws_url}")

        try:
            logger.debug("[WS] Step 1: Connecting to WebSocket...")
            await self._connect_websocket(ws_url)

            logger.debug("[WS] Step 2: Sending Socket.IO connect packet...")
            await self._send_connect_packet()

            logger.debug("[WS] Step 3: Handling connect response...")
            await self._handle_connect_response()

            logger.debug("[WS] Step 4: Sending authentication...")
            await self._send_authentication()

            logger.debug("[WS] Step 5: Starting message listener...")
            self._listen_task = asyncio.create_task(self._listen_messages())
            logger.info("[WS] Connected successfully")
        except Exception as e:
            import traceback

            logger.error(f"[WS] Connection error: {e}")
            logger.error(f"[WS] Traceback: {traceback.format_exc()}")
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Отключение от WebSocket."""
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
        """Регистрирует обработчик для специфических ивентов WebSocket.

        Args:
            event: Название ивента (например, 'rawData', 'rawIncidents', 'breakUpdate')
            handler: Функция для обработки ивента
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    @property
    def is_connected(self) -> bool:
        """Проверка подключен ли WebSocket."""
        return self._ws is not None and not self._ws.closed

    # Context managers
    async def __aenter__(self):
        """Context manager for auto-connect."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager for auto-disconnect."""
        await self.disconnect()
