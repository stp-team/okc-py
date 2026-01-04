"""Lines API repository for OKC."""

import logging

from okc_py.client import Client

from .base import BaseAPI

logger = logging.getLogger(__name__)


class LinesAPI(BaseAPI):
    """HTTP API for Lines endpoints."""

    def __init__(self, client: Client):
        """Initialize Lines API repository.

        Args:
            client: Authenticated OKC API client
        """
        super().__init__(client)
        self.service_url = "appl/chart"
