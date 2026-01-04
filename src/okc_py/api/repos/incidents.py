import logging

from okc_py.api.models.incidents import IncidentDetail, LogFilters
from okc_py.client import Client

from .base import BaseAPI

logger = logging.getLogger(__name__)


class IncidentsAPI(BaseAPI):
    """Взаимодействия с API аварий."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "incidents/api"

    async def get_filters(self, division: str = "stp") -> LogFilters | None:
        """Получает доступные фильтры аварий.

        Args:
            division: Направление. Обязательно к заполнению, стандартно 'stp'
        """
        data = {
            "division": division,
        }
        response = await self.post(f"{self.service_url}/get-log-filters", data=data)

        try:
            result = await response.json()
            return LogFilters.model_validate(result)
        except Exception as e:
            logger.error(f"[Аварии] Ошибка получения фильтров: {e}")
            return None

    async def get_incidents(
        self,
        start_date: str,
        stop_date: str,
        division: str = "stp",
        cities: list[int] | None = None,
        products: list[int] | None = None,
        scales: list[int] | None = None,
        units: list[int] | None = None,
    ) -> list[IncidentDetail] | None:
        """Получает детали аварий по фильтрам.

        Доступные типы продуктов (products):
        - DNS: 19
        - VPN: 18
        - Интернет: 11
        - Офис: 13
        - ППР: 9
        - Прочее: 14
        - Телевидение: 12
        - Телефония: 10

        Args:
            start_date: Начальная дата в формате DD.MM.YYYY
            stop_date: Конечная дата в формате DD.MM.YYYY
            division: Направление. Обязательно к заполнению, стандартно 'stp'
            cities: Список ID городов для фильтрации
            products: Список ID продуктов для фильтрации
            scales: Список ID масштабов для фильтрации
            units: Список ID НТП для фильтрации
        """
        data = {
            "startDate": start_date,
            "stopDate": stop_date,
            "division": division,
            "pickedCities": cities or [],
            "pickedProducts": products or [],
            "pickedScales": scales or [],
            "pickedUnits": units or [],
        }
        response = await self.post(f"{self.service_url}/get-log-details", data=data)

        try:
            result = await response.json()
            return [IncidentDetail.model_validate(item) for item in result]
        except Exception as e:
            logger.error(f"[Аварии] Ошибка получения списка аварий: {e}")
            return None
