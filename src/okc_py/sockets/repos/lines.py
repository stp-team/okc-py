"""Lines WebSocket API for OKC real-time updates."""

import logging
from typing import Literal

from okc_py.client import Client
from okc_py.sockets.repos.base import BaseWebSocketClient

logger = logging.getLogger(__name__)

# Available line namespaces
LineNamespace = Literal[
    "ntp1",  # /ts-line-ntp1-okcdb-ws
    "ntp2",  # /line-ntp2-ws
    "nck",  # /ts-line-genesys-okcdb-ws
]

LINE_NAMESPACES: dict[LineNamespace, str] = {
    "ntp1": "/ts-line-ntp1-okcdb-ws",
    "ntp2": "/line-ntp2-ws",
    "nck": "/ts-line-genesys-okcdb-ws",
}


class LineWSClient(BaseWebSocketClient):
    """WebSocket client for a specific line.

    Real-time events:
    - authRoles: User role information
    - rawIncidents: Incidents (priority, new, old)
    - rawData: Line data (updated every second)
    """

    def __init__(self, client: Client, line: LineNamespace = "nck"):
        """Initialize Line WebSocket client.

        Args:
            client: Authenticated OKC API client
            line: Line identifier (ntp1, ntp2, nck)
        """
        namespace = LINE_NAMESPACES.get(line, LINE_NAMESPACES["nck"])
        super().__init__(client, namespace=namespace)
        self._line = line

    async def _get_auth_cookies(self) -> str:
        """Get authentication cookies for WebSocket connection.

        Returns:
            Cookie header string with all session cookies
        """
        if not self.client._session:
            return ""
        cookie_jar = self.client._session.cookie_jar
        return "; ".join(f"{c.key}={c.value}" for c in cookie_jar)
