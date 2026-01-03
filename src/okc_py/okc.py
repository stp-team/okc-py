"""Main OKC API wrapper class."""

from loguru import logger

from .client import Client
from .config import Settings
from .exceptions import ConfigurationError
from .repos import DossierAPI, PremiumAPI, SlAPI, TestsAPI, TutorsAPI, UreAPI


class OKC:
    """Main OKC API client.

    This is the primary entry point for interacting with the OKC API.
    It provides access to all API categories through dedicated repository objects.

    Example:
        ```python
        import asyncio
        from okc_py import OKC

        async def main():
            async with OKC() as okc:
                # Get dossier information
                dossier = await okc.dossier.get(...)
                print(f"Dossier: {dossier}")

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

        # Initialize API repositories (will be set after connection)
        self.dossier: DossierAPI | None = None
        self.premium: PremiumAPI | None = None
        self.ure: UreAPI | None = None
        self.sl: SlAPI | None = None
        self.tests: TestsAPI | None = None
        self.tutors: TutorsAPI | None = None

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

        # Initialize API repositories
        self.dossier = DossierAPI(self.client)
        self.premium = PremiumAPI(self.client)
        self.ure = UreAPI(self.client)
        self.sl = SlAPI(self.client)
        self.tests = TestsAPI(self.client)
        self.tutors = TutorsAPI(self.client)

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

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.client.is_connected

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self.client.is_authenticated

    async def test_connection(self) -> bool | None:
        """Test the OKC API connection and authentication.

        Returns:
            True if connection and authentication are working, False otherwise
        """
        try:
            if not self.is_connected:
                await self.connect()

            # Test with a simple API call
            if self.dossier:
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
