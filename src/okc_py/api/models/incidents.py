from pydantic import BaseModel, Field


class FilterItem(BaseModel):
    """Базовый элемент фильтра с id и name."""

    id: int
    name: str


class LogFilters(BaseModel):
    """Фильтры для лога аварий."""

    units: list[FilterItem]
    scale_types: list[FilterItem] = Field(alias="scaleTypes")
    cities: list[FilterItem]
    products: list[FilterItem]


class IncidentDetail(BaseModel):
    """Детали аварий."""

    start_date: str = Field(alias="startDate", description="Дата начала аварии")
    end_date: str | None = Field(
        default=None, alias="endDate", description="Дата завершения аварии"
    )
    duration: str = Field(description="Длительность аварии")
    jira_id: str | None = Field(
        default=None, alias="jiraId", description="Идентификатор аварии в Jira"
    )
    units: str | None = Field(default=None, description="Очереди (направления) аварии")
    author_name: str = Field(alias="authorName", description="ФИО открывшего аварию")
    closer_name: str | None = Field(
        default=None, alias="closerName", description="ФИО закрывшего аварию"
    )
    description: str = Field(description="Описание аварии")
    scale: str | None = Field(default=None, description="Масштаб аварии")
    product: str | None = Field(default=None, description="Продукт аварии")
