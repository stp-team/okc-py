# Main OKC client
# Core components (for advanced users)
# API classes (for advanced users who want direct access)
from okc_py.api import DossierAPI, PremiumAPI, SlAPI, TestsAPI, TutorsAPI, UreAPI

from .client import Client
from .config import Settings

# All exceptions
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    CSRFError,
    InvalidCredentialsError,
    NetworkError,
    NotFoundError,
    OKCError,
    RateLimitError,
    ResponseParsingError,
    ServiceUnavailableError,
    SessionError,
)
from .okc import OKC

__version__ = "0.1.0"

__all__ = [
    # Main client
    "OKC",
    # Core components
    "Client",
    "Settings",
    # Exceptions
    "OKCError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "InvalidCredentialsError",
    "CSRFError",
    "ServiceUnavailableError",
    "ConfigurationError",
    "ResponseParsingError",
    "NetworkError",
    "SessionError",
    # API classes
    "DossierAPI",
    "PremiumAPI",
    "UreAPI",
    "SlAPI",
    "TutorsAPI",
    "TestsAPI",
    # Version
    "__version__",
]
