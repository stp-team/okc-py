"""Main OKC API wrapper class."""

import logging

from .client import Client
from .config import Settings
from .exceptions import ConfigurationError
from .sockets.repos.lines import LINE_NAMESPACES, LineNamespace, LineWSClient

logger = logging.getLogger(__name__)


class _APIRouter:
    """Router for HTTP API repositories.

    Provides access to all HTTP API repositories.
    """

    def __init__(self, client: Client):
        """Initialize API router.

        Args:
            client: Authenticated OKC API client
        """
        self._client = client
        self._initialized = False

    def _ensure_initialized(self):
        """Initialize all API repositories if not already done."""
        if self._initialized:
            return

        # Import API classes here to avoid circular imports
        from okc_py.api import (
            DossierAPI,
            PremiumAPI,
            SlAPI,
            TestsAPI,
            TutorsAPI,
            UreAPI,
        )
        from okc_py.api.repos.appeals import AppealsAPI
        from okc_py.api.repos.incidents import IncidentsAPI
        from okc_py.api.repos.lines import LinesAPI
        from okc_py.api.repos.sales import SalesAPI

        # Initialize repositories
        self.dossier = DossierAPI(self._client)
        self.premium = PremiumAPI(self._client)
        self.ure = UreAPI(self._client)
        self.sl = SlAPI(self._client)
        self.tests = TestsAPI(self._client)
        self.tutors = TutorsAPI(self._client)
        self.appeals = AppealsAPI(self._client)
        self.sales = SalesAPI(self._client)
        self.incidents = IncidentsAPI(self._client)
        self.lines = LinesAPI(self._client)

        self._initialized = True

    def __getattr__(self, name: str):
        """Get API repository by name.

        Args:
            name: Repository name (dossier, appeals, lines, etc.)

        Returns:
            API repository instance
        """
        self._ensure_initialized()
        return object.__getattribute__(self, name)


class _WSRouter:
    """Router for WebSocket connections.

    Provides access to WebSocket clients for real-time updates.
    """

    def __init__(self, client: Client):
        """Initialize WebSocket router.

        Args:
            client: Authenticated OKC API client
        """
        self._client = client
        self._lines = _LinesWSRouter(client)

    @property
    def lines(self) -> "_LinesWSRouter":
        """Access Lines WebSocket clients.

        Returns:
            Lines WebSocket router

        Example:
            # Connect to NCK line
            await client.ws.lines.nck.connect()
            client.ws.lines.nck.on("rawData", handler)

            # Connect to NTP1 line
            await client.ws.lines.ntp1.connect()
        """
        return self._lines


class _LinesWSRouter:
    """Router for Lines WebSocket clients.

    Provides access to different line WebSocket clients.
    """

    def __init__(self, client: Client):
        """Initialize Lines WebSocket router.

        Args:
            client: Authenticated OKC API client
        """
        self._client = client
        self._clients: dict[LineNamespace, LineWSClient] = {}

    def __getattr__(self, line: str) -> LineWSClient:
        """Get WebSocket client for a specific line.

        Args:
            line: Line name (ntp1, ntp2, nck)

        Returns:
            LineWSClient instance for the specified line

        Raises:
            ValueError: If line is not supported

        Example:
            ntp1_client = client.ws.lines.ntp1
            nck_client = client.ws.lines.nck
        """
        if line not in LINE_NAMESPACES:
            raise ValueError(
                f"Unknown line: {line}. Available lines: {list(LINE_NAMESPACES.keys())}"
            )

        line_key: LineNamespace = line  # type: ignore

        if line_key not in self._clients:
            self._clients[line_key] = LineWSClient(self._client, line=line_key)

        return self._clients[line_key]


class OKC:
    """Main OKC API client.

    This is the primary entry point for interacting with the OKC API.
    It provides access to all API categories through dedicated router objects.

    Example:
        ```python
        import asyncio
        from okc_py import OKC

        async def main():
            async with OKC() as okc:
                # HTTP API calls
                appeals = await okc.api.appeals.get_filters()
                print(f"Appeals: {appeals}")

                # WebSocket connections
                await okc.ws.lines.nck.connect()
                okc.ws.lines.nck.on("rawData", handler)

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        settings: Settings | None = None,
        **kwargs,
    ):
        """Initialize the OKC API client.

        Args:
            username: OKC username. If not provided, will try to get from OKC_USERNAME env var
            password: OKC password. If not provided, will try to get from OKC_PASSWORD env var
            settings: Optional settings configuration
            **kwargs: Additional arguments passed to Settings

        Raises:
            ConfigurationError: If BASE_URL is not configured
        """
        # Get credentials from parameters or environment
        if not username:
            import os

            username = os.getenv("OKC_USERNAME")

        if not password:
            import os

            password = os.getenv("OKC_PASSWORD")

        # Initialize settings
        if settings is None:
            settings = Settings(**kwargs)

        if not settings.BASE_URL:
            raise ConfigurationError(
                "BASE_URL is required. Set it in Settings or via OKC_BASE_URL env var"
            )

        # Initialize HTTP client
        self.client = Client(username=username, password=password, settings=settings)

        # Initialize routers
        self._api = _APIRouter(self.client)
        self._ws = _WSRouter(self.client)

        # Keep old properties for backward compatibility (deprecated)
        self.dossier = None
        self.premium = None
        self.ure = None
        self.sl = None
        self.tests = None
        self.tutors = None
        self.appeals = None
        self.sales = None
        self.incidents = None
        self.lines = None

        logger.info("OKC API client initialized")

    async def __aenter__(self):
        """Async context manager entry - creates session and authenticates."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes session."""
        await self.close()

    async def connect(self):
        """Manually connect and authenticate.

        Note: This is called automatically when using the async context manager.
        """
        await self.client.connect()

        # Initialize API router (creates all repositories)
        self._api._ensure_initialized()

        # For backward compatibility, set direct properties
        self.dossier = self._api.dossier
        self.premium = self._api.premium
        self.ure = self._api.ure
        self.sl = self._api.sl
        self.tests = self._api.tests
        self.tutors = self._api.tutors
        self.appeals = self._api.appeals
        self.sales = self._api.sales
        self.incidents = self._api.incidents
        self.lines = self._api.lines

        logger.info("OKC API repositories initialized")

    async def close(self):
        """Close the session.

        Note: This is called automatically when using the async context manager.
        """
        await self.client.close()
        self.dossier = None
        self.premium = None
        self.ure = None
        self.sl = None
        self.tests = None
        self.tutors = None
        self.appeals = None
        self.sales = None
        self.incidents = None
        self.lines = None

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.client.is_connected

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self.client.is_authenticated

    @property
    def api(self) -> _APIRouter:
        """Access HTTP API repositories.

        Returns:
            API router for accessing HTTP API repositories

        Example:
            # Access different API repositories
            appeals = await okc.api.appeals.get_filters()
            incidents = await okc.api.incidents.list()
            sales_data = await okc.api.sales.get_report()
        """
        return self._api

    @property
    def ws(self) -> _WSRouter:
        """Access WebSocket connections.

        Returns:
            WebSocket router for accessing WebSocket clients

        Example:
            # Connect to Lines WebSocket
            await okc.ws.lines.nck.connect()
            okc.ws.lines.nck.on("rawData", handler)
        """
        return self._ws

    async def test_connection(self) -> bool | None:
        """Test the OKC API connection and authentication.

        Returns:
            True if connection and authentication are working, False otherwise
        """
        try:
            if not self.is_connected:
                await self.connect()

            # Test with a simple API call
            self._api._ensure_initialized()
            if self._api.dossier:
                logger.info("OKC API connection test successful")
                return True

        except Exception as e:
            logger.error(f"OKC API connection test failed: {e}")
            return False

    def __repr__(self) -> str:
        """String representation of OKC client."""
        status = "connected" if self.is_connected else "disconnected"
        auth_status = "authenticated" if self.is_authenticated else "not authenticated"
        return f"OKC(base_url='{self.client.settings.BASE_URL}', status='{status}', auth='{auth_status}')"
