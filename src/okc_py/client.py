"""Main OKC API client with built-in authentication."""

from typing import Optional
from aiohttp import ClientSession
from loguru import logger

from .auth import authenticate
from .config import Settings
from .repos import SlAPI
from .repos.dossier import DossierAPI
from .repos.ure import UreAPI


class Client:
    """Основной клиент для доступа к API."""

    def __init__(self, settings: Settings):
        """Инициализация клиента.

        Args:
            settings: Объект Settings
        """
        self.settings = settings

        self._session: Optional[ClientSession] = None
        self._authenticated = False
        self.dossier: Optional[DossierAPI] = None
        self.ure: Optional[UreAPI] = None
        self.sl: Optional[SlAPI] = None

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
            self.ure = UreAPI(self._session, self.settings)
            self.sl = SlAPI(self._session, self.settings)
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
        """Убеждаемся, что клиент авторизован перед тем, как делать запросы."""
        if not self._authenticated or not self._session:
            raise RuntimeError(
                "Client not authenticated. Use 'await client.connect()' or async context manager."
            )
