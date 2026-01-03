"""Custom exceptions for OKC API wrapper."""

from typing import Any


class OKCError(Exception):
    """Base OKC API exception."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        """Initialize OKC API error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: API response data if applicable
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(OKCError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(OKCError):
    """Rate limit exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(OKCError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str, message: str | None = None):
        if message is None:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)
        self.resource = resource
        self.identifier = identifier


class InvalidCredentialsError(OKCError):
    """Invalid username or password."""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message, status_code=401)


class CSRFError(OKCError):
    """Failed to obtain CSRF token."""

    def __init__(self, message: str = "Failed to obtain CSRF token"):
        super().__init__(message, status_code=500)


class SessionError(OKCError):
    """Session-related error (not connected, already closed, etc.)."""

    def __init__(self, message: str = "Session error"):
        super().__init__(message)


class ConfigurationError(OKCError):
    """Configuration or setup error."""

    def __init__(self, message: str):
        super().__init__(message)


class ResponseParsingError(OKCError):
    """Error parsing OKC API response."""

    def __init__(self, message: str, raw_response: str | None = None):
        super().__init__(message)
        self.raw_response = raw_response


class NetworkError(OKCError):
    """Network or connection error."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class ServiceUnavailableError(OKCError):
    """OKC API service is temporarily unavailable."""

    def __init__(self, message: str = "OKC API service is temporarily unavailable"):
        super().__init__(message, status_code=503)
