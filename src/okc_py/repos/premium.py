import logging

from loguru import logger

from ..client import Client
from ..models.premium import HeadPremiumResponse, SpecialistPremiumResponse
from .base import BaseAPI


class PremiumAPI(BaseAPI):
    """Взаимодействия с API URE."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "premium"
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_specialist_premium(
        self,
        period: str,
        division: str,
        subdivision_id: list[int] | None = None,
        heads_id: list[int] | None = None,
        employees_id: list[int] | None = None,
    ) -> SpecialistPremiumResponse | None:
        """Получаем показатели премиума специалистов.

        Args:
            period: Выгружаемый период
            division: Направление специалистов
            subdivision_id: Идентификатор направления
            heads_id: Список идентификаторов руководителей
            employees_id: Список идентификаторов сотрудников

        Returns:
            Показатели премиума специалистов, если нашли, иначе None
        """

        if employees_id is None:
            employees_id = []
        if heads_id is None:
            heads_id = []
        if subdivision_id is None:
            subdivision_id = []

        endpoint = ""
        match division:
            case "НТП1":
                endpoint = f"{self.service_url}/ntp1/get-premium-spec-month"
            case "НТП2":
                endpoint = f"{self.service_url}/ntp2/get-premium-spec-month"
            case "НЦК":
                endpoint = f"{self.service_url}/ntp-nck/get-premium-spec-month"

        response = await self.post(
            endpoint=endpoint,
            json={
                "period": period,
                "subdivisionId": subdivision_id,
                "headsId": heads_id,
                "employeesId": employees_id,
            },
        )

        try:
            data = await response.json()
            premium = SpecialistPremiumResponse.model_validate(data)
            return premium
        except Exception as e:
            logger.error(f"[URE] Ошибка получения премиума для специалистов: {e}")
            return None

    async def get_head_premium(
        self,
        period: str,
        division: str,
        subdivision_id: list[int] | None = None,
        heads_id: list[int] | None = None,
        employees_id: list[int] | None = None,
    ) -> HeadPremiumResponse | None:
        """Получаем показатели премиума руководителей.

        Args:
            period: Выгружаемый период
            division: Направление руководителей
            subdivision_id: Идентификатор направления
            heads_id: Список идентификаторов руководителей
            employees_id: Список идентификаторов руководителей

        Returns:
            Показатели премиума руководителей, если нашли, иначе None
        """

        if employees_id is None:
            employees_id = []
        if heads_id is None:
            heads_id = []
        if subdivision_id is None:
            subdivision_id = []

        endpoint = ""
        match division:
            case "НТП":
                endpoint = f"{self.service_url}/ntpo/get-premium-head-month"
            case "НЦК":
                endpoint = f"{self.service_url}/ntp-nck/get-premium-head-month"

        response = await self.post(
            endpoint=endpoint,
            json={
                "period": period,
                "subdivisionId": subdivision_id,
                "headsId": heads_id,
                "employeesId": employees_id,
            },
        )

        try:
            data = await response.json()
            premium = HeadPremiumResponse.model_validate(data)
            return premium
        except Exception as e:
            logger.error(f"[URE] Ошибка получения премиума для руководителей: {e}")
            return None
