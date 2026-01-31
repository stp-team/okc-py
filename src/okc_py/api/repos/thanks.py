"""Repository for thanks (благодарности) API."""

import logging

from ..models.thanks import (
    ThanksReportRequest,
    ThanksReportResponse,
)
from .base import BaseAPI

logger = logging.getLogger(__name__)


class ThanksAPI(BaseAPI):
    """Взаимодействия с API благодарностей."""

    async def get_report(
        self,
        whom_units: list[int] | None = None,
        whom_subdivisions: list[int] | None = None,
        whom_heads: list[int] | None = None,
        whom_employees: list[int] | None = None,
        start_date: str | None = None,
        stop_date: str | None = None,
        init_units: list[int] | None = None,
        init_subdivisions: list[int] | None = None,
        who_processed: list[int] | None = None,
        agreement: str | None = None,
        statuses: list[int] | None = None,
    ) -> ThanksReportResponse | None:
        """Получаем отчёт по благодарностям.

        Args:
            whom_units: Идентификаторы подразделений получателей
            whom_subdivisions: Идентификаторы направлений получателей
            whom_heads: Идентификаторы руководителей получателей
            whom_employees: Идентификаторы сотрудников получателей
            start_date: Начальная дата в формате DD.MM.YYYY
            stop_date: Конечная дата в формате DD.MM.YYYY
            init_units: Идентификаторы подразделений инициаторов
            init_subdivisions: Идентификаторы направлений инициаторов
            who_processed: Идентификаторы обработчиков
            agreement: Номер договора
            statuses: Список статусов (2 - подтверждено)

        Returns:
            Список благодарностей, если нашли, иначе None
        """
        if whom_units is None:
            whom_units = []
        if whom_subdivisions is None:
            whom_subdivisions = []
        if whom_heads is None:
            whom_heads = []
        if whom_employees is None:
            whom_employees = []
        if init_units is None:
            init_units = []
        if init_subdivisions is None:
            init_subdivisions = []
        if who_processed is None:
            who_processed = []
        if statuses is None:
            statuses = []

        response = await self.post(
            endpoint="/yii/appl/thanks/get-report",
            json={
                "whomUnits": whom_units,
                "whomSubdivisions": whom_subdivisions,
                "whomHeads": whom_heads,
                "whomEmployees": whom_employees,
                "startDate": start_date,
                "stopDate": stop_date,
                "initUnits": init_units,
                "initSubdivisions": init_subdivisions,
                "whoProcessed": who_processed,
                "agreement": agreement,
                "statuses": statuses,
            },
        )

        try:
            data = await response.json()
            report = ThanksReportResponse.model_validate(data)
            return report
        except Exception as e:
            logger.error(f"[Thanks] Ошибка получения отчёта по благодарностям: {e}")
            return None

    async def get_report_by_request(
        self, request: ThanksReportRequest
    ) -> ThanksReportResponse | None:
        """Получаем отчёт по благодарностям используя модель запроса.

        Args:
            request: Модель запроса с фильтрами

        Returns:
            Список благодарностей, если нашли, иначе None
        """
        response = await self.post(
            endpoint="/yii/appl/thanks/get-report",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        try:
            data = await response.json()
            report = ThanksReportResponse.model_validate(data)
            return report
        except Exception as e:
            logger.error(f"[Thanks] Ошибка получения отчёта по благодарностям: {e}")
            return None
