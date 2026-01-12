"""Lines API repository for OKC."""

import logging

from ...client import Client
from ..models.lines import LineMessage, UserData
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

    async def get_day_log(
        self,
        line_app_id: str | int,
    ) -> list[LineMessage] | None:
        data = {
            "lineAppId": line_app_id,
        }
        response = await self.post("/api/line-message/get-day-log", data=data)

        try:
            result = await response.json()
            return [LineMessage.model_validate(item) for item in result]
        except Exception as e:
            logger.error(f"[Линии] Ошибка получения лога: {e}")
            return None

    async def get_user_data(
        self, employee_id: str | int, tz: str | int = 0
    ) -> UserData | None:
        data = {
            "employeeId": employee_id,
            "tz": tz,
        }
        response = await self.post("/api/user-info/get-user-data", data=data)

        try:
            result = await response.json()
            return UserData.model_validate(result)
        except Exception as e:
            logger.error(f"[Линии] Ошибка получения данных пользователя: {e}")
            return None

    async def send_example(self, line_app_id: str | int, message: str) -> bool:
        data = {
            "lineAppId": line_app_id,
            "message": message,
        }
        response = await self.post(
            "/api/line-mail-example/send-example-mail", data=data
        )

        try:
            result = await response.json()
            return result.get("success") is True
        except Exception as e:
            logger.error(f"[Линии] Ошибка отправки примера: {e}")
            return False
