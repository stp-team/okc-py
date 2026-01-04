import logging

from pydantic import TypeAdapter

from okc_py.api.models.dossier import Employee, EmployeeData
from okc_py.client import Client

from .base import BaseAPI

logger = logging.getLogger(__name__)


class DossierAPI(BaseAPI):
    """Взаимодействия с API профайла."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "dossier/api"

    async def get_employees(self, exclude_fired: bool = False) -> list[Employee] | None:
        """Получает сотрудников из профайла.

        Args:
            exclude_fired: Исключить ли уволенных

        Returns:
            Список сотрудников
        """
        adapter = TypeAdapter(list[Employee])

        response = await self.post(f"{self.service_url}/get-employees")

        try:
            data = await response.json()

            employees = adapter.validate_python(data)

            if exclude_fired:
                employees = [e for e in employees if not e.fired_date]

            return employees
        except Exception as e:
            logger.error(f"[Профайл] Ошибка получения списка специалистов: {e}")
            return None

    async def get_employee(
        self,
        employee_id: int | None = None,
        employee_fullname: str | None = None,
        show_kpi: bool = True,
        show_criticals: bool = True,
    ) -> EmployeeData | None:
        """Получает сотрудника по ФИО или идентификатору.

        Args:
            employee_id: Идентификатор сотрудника на OKC
            employee_fullname: ФИО сотрудника
            show_kpi: Получать ли показатели сотрудника
            show_criticals: Получать ли критические ошибки сотрудника

        Returns:
            Информация о сотруднике, если найден, иначе None
        """
        if employee_id is None and employee_fullname:
            employees = await self.get_employees()
            if not employees:
                return None

            for employee in employees:
                if employee.fullname == employee_fullname:
                    employee_id = employee.id
                    break

        if employee_id is None:
            return None

        response = await self.post(
            endpoint=f"{self.service_url}/get-dossier",
            json={
                "employee": employee_id,
                "showKpi": show_kpi,
                "showCriticals": show_criticals,
            },
        )

        try:
            data = await response.json()
            employee = EmployeeData.model_validate(data)
            return employee
        except Exception as e:
            logger.error(f"[Профайл] Ошибка получения специалиста: {e}")
            return None
