import logging
from typing import Any

from ...client import Client
from ..models.sales import SalesFilters, SalesFiltersByDate, SalesReport
from .base import BaseAPI

logger = logging.getLogger(__name__)


class SalesAPI(BaseAPI):
    """Взаимодействия с API продаж."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "sales/report"

    async def get_filters(self) -> SalesFilters | None:
        """Получить доступные фильтры для отчёта по продажам.

        Returns:
            SalesFilters объект с доступными опциями фильтрации или None при ошибке
        """
        response = await self.post(f"{self.service_url}/get-filters")

        try:
            result = await response.json()
            return SalesFilters.model_validate(result)
        except Exception as e:
            logger.error(f"[Продажи] Ошибка получения фильтров: {e}")
            return None

    async def get_filters_by_date(
        self, start_date: str, stop_date: str
    ) -> SalesFiltersByDate | None:
        """Получить доступные фильтры для отчёта по продажам за период.

        Args:
            start_date: Начальная дата в формате DD.MM.YYYY
            stop_date: Конечная дата в формате DD.MM.YYYY

        Returns:
            SalesFiltersByDate объект с руководителями и сотрудниками или None при ошибке
        """
        data = {
            "startDate": start_date,
            "stopDate": stop_date,
        }
        response = await self.post(f"{self.service_url}/get-filters-by-date", json=data)

        try:
            result = await response.json()
            return SalesFiltersByDate.model_validate(result)
        except Exception as e:
            logger.error(f"[Продажи] Ошибка получения фильтров по дате: {e}")
            return None

    async def get_report(
        self,
        units: list[int],
        sales_types: list[str],
        start_date: str,
        stop_date: str,
        employees: list[str] | None = None,
        heads: list[str] | None = None,
        subdivisions: list[str] | None = None,
        is_loan: bool | None = None,
    ) -> SalesReport | None:
        """Получить отчёт по продажам.

        Доступные типы продаж (sales_types):
        - SaleMaterialsEns: Оборудование
        - SaleTestDrive: Тест-драйв
        - SalePPDRequests: Платный сервис
        - SalePaidService: Выполненный удаленный платный сервис
        - SaleVAS: VAS
        - SaleAgreements: Договоры
        - Sale100Plus: Переключения 100+

        Args:
            units: Список ID подразделений
            sales_types: Список типов продаж (SaleMaterialsEns, SaleTestDrive, SalePPDRequests)
            start_date: Начальная дата в формате DD.MM.YYYY
            stop_date: Конечная дата в формате DD.MM.YYYY
            employees: Список ФИО сотрудников для фильтрации
            heads: Список ФИО руководителей для фильтрации
            subdivisions: Список подразделений для фильтрации
            is_loan: Фильтр по кредиту (True/False)

        Returns:
            SalesReport объект с данными отчёта или None при ошибке
        """
        data = {
            "units": units,
            "salesTypes": sales_types,
            "startDate": start_date,
            "stopDate": stop_date,
            "employees": employees or [],
            "heads": heads or [],
            "subdivisions": subdivisions or [],
            "isLoan": is_loan,
        }
        response = await self.post(f"{self.service_url}/get-report", json=data)

        try:
            result: Any = await response.json()
            return SalesReport.model_validate(result[0])
        except Exception as e:
            logger.error(f"[Продажи] Ошибка получения отчета: {e}")
            return None
