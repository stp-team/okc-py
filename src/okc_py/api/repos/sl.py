import logging

from okc_py.api.models.sl import ReportData, SlRootModel
from okc_py.client import Client

from .base import BaseAPI

logger = logging.getLogger(__name__)


class SlAPI(BaseAPI):
    """Взаимодействия с API SL."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "genesys/ntp"

    async def get_vq_chat_filter(self) -> SlRootModel | None:
        """Получает доступные фильтры статистики SL.

        Returns:
            Список доступных фильтров, если нашли, иначе None
        """
        response = await self.post(endpoint=f"{self.service_url}/get-vq-chat-filter")
        try:
            data = await response.json()
            return SlRootModel.model_validate(data)
        except Exception as e:
            logger.error(f"[SL] Ошибка получения фильтров SL: {e}")
            return None

    async def get_sl(
        self,
        start_date: str,
        stop_date: str,
        units: int | list[int],
        queues: list[str],
    ) -> ReportData | None:
        """Получает статистику SL.

        Args:
            start_date: День начала периода
            stop_date: День конца периода
            units: Идентификатор(ы) направлений
            queues: Идентификаторы линий

        Returns:
            Статистика SL за указанный период
        """
        units_list = units if isinstance(units, list) else [units]

        payload = {
            "startDate": start_date,
            "stopDate": stop_date,
            "units": units_list,
            "queues": queues,
        }

        response = await self.post(
            endpoint=f"{self.service_url}/get-chat-sl-report",
            json=payload,
        )

        try:
            data = await response.json()
            return ReportData.model_validate(data)
        except Exception as e:
            logger.error(f"[SL] Ошибка получения SL: {e}")
            return None
