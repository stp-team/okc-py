from urllib.parse import urlencode

from loguru import logger
from pydantic import TypeAdapter

from ..client import Client
from ..models.tests import (
    AssignedTest,
    Test,
    TestCategory,
    TestDetailedTheme,
    TestsSubdivision,
    TestsSupervisor,
    TestsUser,
)
from .base import BaseAPI


class TestsAPI(BaseAPI):
    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "testing/api"

    async def get_tests(self) -> list[Test] | None:
        adapter = TypeAdapter(list[Test])

        response = await self.post(
            f"{self.service_url}/get-tests",
        )

        try:
            data = await response.json()
            tests = adapter.validate_python(data)
            return tests
        except Exception as e:
            logger.error(f"[Tests] Error parsing tests: {e}")
            return None

    async def get_assigned_tests(
        self, start_date: str, stop_date: str, subdivisions: list[int] | None = None
    ) -> list[AssignedTest] | None:
        """
        Получить список назначенных тестов.

        Args:
            start_date: Дата начала в формате DD.MM.YYYY
            stop_date: Дата окончания в формате DD.MM.YYYY
            subdivisions: Список ID подразделений

        Returns:
            Список назначенных тестов или None в случае ошибки
        """
        adapter = TypeAdapter(list[AssignedTest])

        # Подготовка данных формы в URL-encoded формате
        form_params = [
            ("startDate", start_date),
            ("stopDate", stop_date),
        ]

        # Добавляем подразделения в формате subdivisions[]=id
        if subdivisions:
            for subdivision_id in subdivisions:
                form_params.append(("subdivisions[]", str(subdivision_id)))

        # Кодируем данные в URL-encoded формат
        encoded_data = urlencode(form_params)

        # Заголовки для form-encoded запроса
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        # Отправляем POST запрос с данными формы
        response = await self.post(
            f"{self.service_url}/get-assigned-tests",
            data=encoded_data.encode("utf-8"),
            headers=headers,
        )

        try:
            data = await response.json()
            tests = adapter.validate_python(data)
            return tests
        except Exception as e:
            logger.error(f"[Tests] Error parsing assigned tests: {e}")
            return None

    async def get_themes(self) -> list[TestDetailedTheme] | None:
        adapter = TypeAdapter(list[TestDetailedTheme])

        response = await self.post(
            f"{self.service_url}/get-themes",
        )

        try:
            data = await response.json()
            themes = adapter.validate_python(data)
            return themes
        except Exception as e:
            logger.error(f"[Tests] Error parsing themes: {e}")
            return None

    async def get_categories(self) -> list[TestCategory] | None:
        adapter = TypeAdapter(list[TestCategory])

        response = await self.post(
            f"{self.service_url}/get-categories",
        )

        try:
            data = await response.json()
            categories = adapter.validate_python(data)
            return categories
        except Exception as e:
            logger.error(f"[Tests] Error parsing categories response: {e}")
            return None

    async def get_users(self) -> list[TestsUser] | None:
        adapter = TypeAdapter(list[TestsUser])

        response = await self.post(
            f"{self.service_url}/get-users",
        )

        try:
            data = await response.json()
            users = adapter.validate_python(data)
            return users
        except Exception as e:
            logger.error(f"[Tests] Error parsing users response: {e}")
            return None

    async def get_supervisors(self) -> list[TestsSupervisor] | None:
        adapter = TypeAdapter(list[TestsSupervisor])

        response = await self.post(
            f"{self.service_url}/get-supervisers",
        )

        try:
            data = await response.json()
            supervisors = adapter.validate_python(data)
            return supervisors
        except Exception as e:
            logger.error(f"[Tests] Error parsing supervisors response: {e}")
            return None

    async def get_subdivisions(self) -> list[TestsSubdivision] | None:
        adapter = TypeAdapter(list[TestsSubdivision])

        response = await self.post(
            f"{self.service_url}/get-subdivisions",
        )

        try:
            data = await response.json()
            subdivisions = adapter.validate_python(data)
            return subdivisions
        except Exception as e:
            logger.error(f"[Tests] Error parsing subdivisions response: {e}")
            return None
