"""Base repository class for OKC API endpoints."""

from typing import Any

from ... import Client


class _ResponseWrapper:
    """Wrapper to mimic aiohttp ClientResponse interface."""

    def __init__(self, data: dict[str, Any] | str, status: int = 200):
        self._data = data
        self.status = status

    async def json(self) -> Any:
        """Return the data as-is (already parsed)."""
        return self._data

    async def text(self) -> str:
        """Return data as string."""
        if isinstance(self._data, str):
            return self._data
        return str(self._data)


class BaseAPI:
    """Base class for all OKC API repositories."""

    def __init__(self, client: Client):
        """Initialize the base API repository.

        Args:
            client: Authenticated OKC API client
        """
        self.client = client
        self.base_url = client.settings.BASE_URL.rstrip("/")
        self.session = client._session

    def _build_url(self, endpoint: str) -> str:
        """Build OKC API URL.

        Args:
            endpoint: API endpoint path

        Returns:
            Complete OKC API URL

        Example:
            _build_url("/api/dossier")
            -> "https://okc.example.com/api/dossier"
        """
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return self.base_url + endpoint

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Make authenticated request to OKC API.

        Args:
            method: HTTP method ("GET", "POST", "PUT", "DELETE")
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            **kwargs: Additional request parameters

        Returns:
            JSON response data or text response
        """
        url = self._build_url(endpoint)

        return await self.client.request(
            method, url, params=params, data=data, **kwargs
        )

    # Convenience methods for common HTTP operations (returning parsed data)
    async def _get_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Convenience method for GET requests."""
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def _post_request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Convenience method for POST requests."""
        return await self._request("POST", endpoint, data=data, **kwargs)

    async def _put_request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Convenience method for PUT requests."""
        return await self._request("PUT", endpoint, data=data, **kwargs)

    async def _delete_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any] | str:
        """Convenience method for DELETE requests."""
        return await self._request("DELETE", endpoint, params=params, **kwargs)

    # HTTP methods returning response-like objects (for backward compatibility)
    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> _ResponseWrapper:
        """Make GET request, returns response wrapper with .json() method."""
        data = await self._get_request(endpoint, params=params, **kwargs)
        return _ResponseWrapper(data)

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: Any = None,
        **kwargs,
    ) -> _ResponseWrapper:
        """Make POST request, returns response wrapper with .json() method.

        Args:
            endpoint: API endpoint
            json: JSON payload
            data: Form data (can be dict or list of tuples for form-encoded)
            **kwargs: Additional arguments
        """
        url = self._build_url(endpoint)

        # Use json parameter for client.request
        if json is not None:
            result = await self.client.request("POST", url, json=json, **kwargs)
        else:
            result = await self.client.request("POST", url, data=data, **kwargs)

        return _ResponseWrapper(result)

    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        **kwargs,
    ) -> _ResponseWrapper:
        """Make PUT request, returns response wrapper with .json() method."""
        data = await self._put_request(endpoint, data=json, **kwargs)
        return _ResponseWrapper(data)

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> _ResponseWrapper:
        """Make DELETE request, returns response wrapper with .json() method."""
        data = await self._delete_request(endpoint, params=params, **kwargs)
        return _ResponseWrapper(data)
