import logging
from urllib.parse import urlencode

from ...client import Client
from ..models.tutors import GraphFiltersResponse, TutorGraphResponse
from .base import BaseAPI

logger = logging.getLogger(__name__)


class TutorsAPI(BaseAPI):
    """Взаимодействия с API наставников."""

    def __init__(self, client: Client):
        super().__init__(client)
        self.service_url = "tutor-graph/tutor-api"

    async def get_filters(self, division_id: int) -> GraphFiltersResponse | None:
        """
        Get graph filters data including all tutors, units, shift types, and tutor types.

        Returns:
            GraphFiltersResponse containing lists of tutors, units, shift types, and tutor types
        """
        form_data = [("divisionId", str(division_id))]

        # Override headers for form data
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await self.post(
            f"{self.service_url}/get-graph-filters", data=form_data, headers=headers
        )

        if response.status != 200:
            return None

        try:
            data = await response.json()
            graph_filters = GraphFiltersResponse.model_validate(data)
            return graph_filters
        except Exception as e:
            logger.error(f"[Наставники] Ошибка получения фильтров графика: {e}")
            return None

    async def get_full_graph(
        self,
        division_id: int,
        start_date: str,
        stop_date: str,
        picked_units: list[int],
        picked_tutor_types: list[int],
        picked_shift_types: list[int],
        tz: int = 0,
    ) -> TutorGraphResponse | None:
        """
        Получает полный график наставников.

        Args:
            division_id: Идентификатор направления
            start_date: Дата начала выгрузки в формате DD.MM.YYYY
            stop_date: Дата конца выгрузки в формате DD.MM.YYYY
            picked_units: Список направлений
            picked_tutor_types: Список типов наставников
            picked_shift_types: Список типов смен
            tz: Timezone offset (default: 0)
        """
        # Prepare form data following the pattern from tests.py
        form_params = [
            ("tz", str(tz)),
            ("divisionId", str(division_id)),
            ("startDate", start_date),
            ("stopDate", stop_date),
        ]

        # Add array parameters using [] suffix
        for unit in picked_units:
            form_params.append(("pickedUnits[]", str(unit)))
        for tutor_type in picked_tutor_types:
            form_params.append(("pickedTutorTypes[]", str(tutor_type)))
        for shift_type in picked_shift_types:
            form_params.append(("pickedShiftTypes[]", str(shift_type)))

        # Encode data as URL-encoded string
        encoded_data = urlencode(form_params)

        # Headers for form-encoded request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        response = await self.post(
            f"{self.service_url}/get-full-graph",
            data=encoded_data.encode("utf-8"),
            headers=headers,
        )

        if response.status != 200:
            return None

        try:
            data = await response.json()
            return TutorGraphResponse.model_validate(data)
        except Exception as e:
            logger.error(f"[Наставники] Ошибка получения графика наставников: {e}")
            return None
