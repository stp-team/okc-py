"""API вебсокетов для отслеживания состояния линий."""

import logging
from typing import Any, Literal

from okc_py.client import Client
from okc_py.sockets.repos.base import BaseWS

logger = logging.getLogger(__name__)

LineNamespace = Literal[
    "ntp1",
    "ntp2",
    "nck",
]

LINE_NAMESPACES: dict[LineNamespace, str] = {
    "ntp1": "/ts-line-ntp1-okcdb-ws",
    "ntp2": "/line-ntp2-ws",
    "nck": "/ts-line-genesys-okcdb-ws",
}


class LineWSClient(BaseWS):
    """Клиент вебсокета для состояния линий.

    Ивенты:
    - authRoles: Информация об авторизованном пользователе
    - rawIncidents: Аварии (приоритетные, новые, старые)
    - rawData: Line data (updated every second)

    Example:
        ```python
        line = LineWSClient(client, "nck")
        await line.connect()

        # Register handlers
        line.on("rawData", lambda data: print(f"Data: {data}"))
        line.on("rawIncidents", lambda data: print(f"Incidents: {data}"))
        ```
    """

    def __init__(self, client: Client, line: LineNamespace = "nck") -> None:
        """Initialize Line WebSocket client.

        Args:
            client: Authenticated OKC API client
            line: Line identifier (ntp1, ntp2, nck)
        """
        self._line = line
        super().__init__(client)

    @property
    def service_url(self) -> str:
        """Get the WebSocket service URL for this line."""
        return LINE_NAMESPACES.get(self._line, LINE_NAMESPACES["nck"])

    async def on_message(self, data: Any) -> None:
        """Handle Line-specific event messages.

        Line events:
        - authRoles: User authentication and role information
        - rawIncidents: Incident data (priority incidents, new incidents, old incidents)
        - rawData: Real-time line statistics and metrics (updated ~1 second)

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

        # Log line-specific events
        if event_data and isinstance(event_data, dict):
            if event == "authRoles":
                logger.debug(f"[Line:{self._line}] Auth roles received")
            elif event == "rawIncidents":
                incident_count = (
                    len(event_data.get("priorityIncidents", []))
                    + len(event_data.get("newIncidents", []))
                    + len(event_data.get("oldIncidents", []))
                )
                logger.info(f"[Line:{self._line}] Incidents update: {incident_count}")
            elif event == "rawData":
                logger.debug(f"[Line:{self._line}] Line data received")
            else:
                logger.debug(f"[Line:{self._line}] Unknown event: {event}")
        else:
            logger.debug(f"[Line:{self._line}] Event: {event}, data: {event_data}")

        # Emit to registered handlers
        self._emit_event(event, event_data)
