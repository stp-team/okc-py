"""Async HTTP client with OKC API authentication and error handling."""

import asyncio
import logging
import time
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientSession, ClientTimeout

from .auth import authenticate
from .config import Settings, setup_logging
from .exceptions import AuthenticationError, NetworkError

logger = logging.getLogger(__name__)


class Client:
    """Async HTTP client with OKC API authentication."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        settings: Settings | None = None,
    ):
        """Initialize the client.

        Args:
            username: OKC username for authentication
            password: OKC password for authentication
            settings: Optional settings configuration
        """
        self.username = username
        self.password = password
        self.settings = settings or Settings()
        self._session: ClientSession | None = None
        self._authenticated = False
        self._last_request_time = 0.0

        # Setup logging
        setup_logging(self.settings.LOG_LEVEL)

    async def __aenter__(self):
        """Async context manager entry - creates session."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes session."""
        await self.close()

    async def connect(self):
        """Initialize aiohttp session and authenticate."""
        if self._session and not self._session.closed:
            return

        timeout = ClientTimeout(total=self.settings.REQUEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=100)

        self._session = ClientSession(
            timeout=timeout,
            connector=connector,
        )

        # Authenticate if credentials provided
        if self.username and self.password:
            await self._authenticate()

        logger.info("OKC API client connected")

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("OKC API client disconnected")

    async def _authenticate(self):
        """Perform OKC authentication."""
        if not self.username or not self.password:
            raise AuthenticationError(
                "Username and password are required for authentication"
            )

        if not self._session:
            raise RuntimeError("Session not initialized")

        await authenticate(
            username=self.username,
            password=self.password,
            session=self._session,
            base_url=self.settings.BASE_URL,
        )
        self._authenticated = True

    async def _rate_limit(self):
        """Apply rate limiting if enabled."""
        if not self.settings.RATE_LIMIT_ENABLED:
            return

        now = time.time()
        time_since_last = now - self._last_request_time
        min_interval = 1.0 / self.settings.REQUESTS_PER_SECOND

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)

        self._last_request_time = time.time()

    async def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Make authenticated request to OKC API.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Complete URL to request
            params: Query parameters
            data: Form data
            json: JSON data (sets Content-Type: application/json)
            **kwargs: Additional aiohttp parameters

        Returns:
            JSON response data or text response

        Raises:
            NetworkError: On HTTP errors
            AuthenticationError: On authentication failures
        """
        if not self._session:
            await self.connect()

        # Apply rate limiting
        await self._rate_limit()

        # Retry logic
        last_exception = None
        for attempt in range(self.settings.MAX_RETRIES + 1):
            try:
                # Use json parameter if provided, otherwise use data
                req_kwargs = {"params": params, **kwargs}
                if json is not None:
                    req_kwargs["json"] = json
                    # Ensure proper headers for JSON requests
                    req_kwargs.setdefault("headers", {})["Accept"] = (
                        "application/json, text/plain, */*"
                    )
                    logger.debug(f"Request: {method} {url} | JSON: {json}")
                else:
                    req_kwargs["data"] = data
                    logger.debug(f"Request: {method} {url} | Data: {data}")

                async with self._session.request(method, url, **req_kwargs) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        retry_after = float(
                            response.headers.get(
                                "Retry-After", str(self.settings.RETRY_DELAY)
                            )
                        )
                        logger.warning(
                            f"Rate limited, sleeping for {retry_after} seconds"
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    # Check for authentication errors
                    if response.status == 401:
                        raise AuthenticationError("Authentication failed")

                    # Raise for HTTP errors
                    response.raise_for_status()

                    # Try to parse JSON response
                    try:
                        result = await response.json()
                        return result
                    except (ValueError, aiohttp.ContentTypeError):
                        # Return text if not JSON
                        result = await response.text()
                        return result

            except ClientError as e:
                last_exception = e
                if attempt < self.settings.MAX_RETRIES:
                    sleep_time = self.settings.RETRY_DELAY * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {sleep_time} seconds: {e}"
                    )
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(
                        f"Request failed after {self.settings.MAX_RETRIES + 1} attempts: {e}"
                    )

        raise NetworkError(f"Request failed: {last_exception}") from last_exception

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._session is not None and not self._session.closed

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated

    def get_cookies(self) -> str:
        """Get authentication cookies as a semicolon-separated string.

        Returns:
            Cookie header string with all session cookies, or empty string if
            no session exists.
        """
        if not self._session:
            return ""
        return "; ".join(f"{c.key}={c.value}" for c in self._session.cookie_jar)

    def get_session(self) -> ClientSession | None:
        """Get the underlying aiohttp session.

        Returns:
            The ClientSession instance or None if not connected.
        """
        return self._session
