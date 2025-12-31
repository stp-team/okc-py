"""Main OKC API client with built-in authentication."""

from typing import Optional
from aiohttp import ClientSession
from loguru import logger

from .auth import authenticate
from .config import Settings
from .repos.dossier import DossierAPI


class Client:
    """Main OKC API client that handles authentication and session management."""

    def __init__(self, settings: Optional[Settings] = None, **kwargs):
        """Initialize the OKC client.

        Args:
            settings: Settings object or None to load from environment
            **kwargs: Override specific settings (BASE_URL, USERNAME, PASSWORD)
        """
        if settings is None:
            # Allow overriding specific settings
            env_settings = Settings()
            self.settings = Settings(
                BASE_URL=kwargs.get("BASE_URL", env_settings.BASE_URL),
                USERNAME=kwargs.get("USERNAME", env_settings.USERNAME),
                PASSWORD=kwargs.get("PASSWORD", env_settings.PASSWORD),
            )
        else:
            self.settings = settings

        self._session: Optional[ClientSession] = None
        self._authenticated = False
        self.dossier: Optional[DossierAPI] = None

    async def __aenter__(self):
        """Async context manager entry - creates session and authenticates."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes session."""
        await self.close()

    async def connect(self):
        """Manually connect and authenticate."""
        if self._session and not self._session.closed:
            return

        self._session = ClientSession()

        try:
            await authenticate(
                username=self.settings.USERNAME,
                password=self.settings.PASSWORD,
                session=self._session,
                base_url=self.settings.BASE_URL,
            )
            self._authenticated = True
            self.dossier = DossierAPI(self._session, self.settings)
            logger.info("Successfully authenticated with OKC API")
        except Exception as e:
            await self._session.close()
            self._session = None
            raise RuntimeError(f"Authentication failed: {e}")

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
            self._authenticated = False
            self.dossier = None

    def _ensure_authenticated(self):
        """Ensure client is authenticated before API calls."""
        if not self._authenticated or not self._session:
            raise RuntimeError(
                "Client not authenticated. Use 'await client.connect()' or async context manager."
            )
