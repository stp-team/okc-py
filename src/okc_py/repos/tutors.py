import logging

from loguru import logger

from .base import BaseAPI
from ..config import Settings
from ..models.tutors import TutorGraphResponse, GraphFiltersResponse


class TutorsAPI(BaseAPI):
    """Взаимодействия с API наставников."""

    def __init__(self, session, settings: Settings):
        super().__init__(session, settings)
        self.service_url = "tutor-graph/tutor-api"
        self.logger = logging.getLogger(self.__class__.__name__)

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
        # Prepare form data as a list of tuples to handle multiple values for the same key
        form_data = [
            ("tz", str(tz)),
            ("divisionId", str(division_id)),
            ("startDate", start_date),
            ("stopDate", stop_date),
        ]

        # Add array parameters
        for unit in picked_units:
            form_data.append(("pickedUnits[]", str(unit)))
        for tutor_type in picked_tutor_types:
            form_data.append(("pickedTutorTypes[]", str(tutor_type)))
        for shift_type in picked_shift_types:
            form_data.append(("pickedShiftTypes[]", str(shift_type)))

        # Override headers for form data
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await self.post(
            f"{self.service_url}/get-full-graph", data=form_data, headers=headers
        )

        if response.status != 200:
            return None

        try:
            data = await response.json()
            tutor_graph = TutorGraphResponse.model_validate(data)
            return tutor_graph
        except Exception as e:
            logger.error(f"[Tutors] Ошибка получения графика наставников: {e}")
            return None

    async def get_graph_filters(self, division_id: int) -> GraphFiltersResponse | None:
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
            logger.error(f"[Tutors] Ошибка получения фильтров графика: {e}")
            return None
