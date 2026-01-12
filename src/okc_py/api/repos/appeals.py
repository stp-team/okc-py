import logging

from ... import Client
from ..models.appeals import (
    AppealsByCityResponse,
    AppealsByProblemResponse,
    DetailsByCityResponse,
    DetailsByProblemResponse,
    FiltersResponse,
)
from .base import BaseAPI

logger = logging.getLogger(__name__)


class AppealsAPI(BaseAPI):
    """Взаимодействия с API обращений."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "appl/chart"

    async def get_filters(self) -> FiltersResponse | None:
        response = await self.post(f"{self.service_url}/get-filters")

        try:
            data = await response.json()
            return FiltersResponse.model_validate(data)
        except Exception as e:
            logger.error(f"[Обращения] Ошибка получения фильтров: {e}")
            return None

    async def get_appeals_by_city(
        self, unit: str, interval: str
    ) -> AppealsByCityResponse | None:
        """Получает обращения по городам.

        Args:
            unit: Единица измерения/подразделение
            interval: Временной интервал

        Returns:
            Список обращений по городам
        """
        data = {
            "unit": unit,
            "interval": interval,
        }
        response = await self.post(f"{self.service_url}/get-appeals-by-city", data=data)

        try:
            data = await response.json()
            return AppealsByCityResponse.model_validate(data)
        except Exception as e:
            logger.error(f"[Обращения] Ошибка получения обращений по городам: {e}")
            return None

    async def get_appeals_by_problem(
        self, unit: str, interval: str
    ) -> AppealsByProblemResponse | None:
        """Получает обращения по типам проблем.

        Args:
            unit: Единица измерения/подразделение
            interval: Временной интервал

        Returns:
            Список обращений по типам проблем
        """
        data = {
            "unit": unit,
            "interval": interval,
        }
        response = await self.post(
            f"{self.service_url}/get-appeals-by-problem", data=data
        )

        try:
            data = await response.json()
            return AppealsByProblemResponse.model_validate(data)
        except Exception as e:
            logger.error(
                f"[Обращения] Ошибка получения обращений по типам проблем: {e}"
            )
            return None

    async def get_details_by_city(
        self, unit: str, interval: str, problem_class: str, city: str
    ) -> DetailsByCityResponse | None:
        """Получает детализированную информацию об обращениях по городу.

        Args:
            unit: Единица измерения/подразделение
            interval: Временной интервал
            problem_class: Класс проблемы
            city: Город

        Returns:
            Детализированный список обращений по городу
        """
        data = {
            "unit": unit,
            "interval": interval,
            "problemClass": problem_class,
            "city": city,
        }
        response = await self.post(f"{self.service_url}/get-details-by-city", data=data)

        try:
            data = await response.json()
            return DetailsByCityResponse.model_validate(data)
        except Exception as e:
            logger.error(
                f"[Обращения] Ошибка получения деталей обращений по городу: {e}"
            )
            return None

    async def get_details_by_problem(
        self, unit: str, interval: str, problem_class: str, city: str
    ) -> DetailsByProblemResponse | None:
        """Получает детализированную информацию об обращениях по проблеме.

        Args:
            unit: Единица измерения/подразделение
            interval: Временной интервал
            problem_class: Класс проблемы
            city: Город

        Returns:
            Детализированный список обращений по проблеме
        """
        data = {
            "unit": unit,
            "interval": interval,
            "problemClass": problem_class,
            "city": city,
        }
        response = await self.post(
            f"{self.service_url}/get-details-by-problem", data=data
        )

        try:
            data = await response.json()
            return DetailsByProblemResponse.model_validate(data)
        except Exception as e:
            logger.error(
                f"[Обращения] Ошибка получения деталей обращений по проблеме: {e}"
            )
            return None
