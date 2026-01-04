from typing import TypeVar

from pydantic import BaseModel, Field, RootModel

T = TypeVar("T")


class _ListResponse(RootModel[list[T]]):
    """Базовый класс для списковых ответов API."""

    root: list[T] = Field(default_factory=list)

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __repr__(self):
        return repr(self.root)

    def __str__(self):
        return str(self.root)


class Unit(BaseModel):
    """Единица измерения/подразделение."""

    id: str
    name: str


class FiltersResponse(BaseModel):
    """Список единиц измерения/подразделений."""

    units: list[Unit]


class CityAppeal(BaseModel):
    """Статистика обращений по городу."""

    id: str = Field(description="Идентификатор города")
    name: str = Field(description="Название города")
    target_name: str = Field(alias="targetName")
    count: int = Field(alias="y", description="Количество обращений по городу")

    model_config = {"populate_by_name": True}


class AppealsByCityResponse(_ListResponse[CityAppeal]):
    """Список обращений по городам."""


class ProblemAppeal(BaseModel):
    """Статистика обращений по типу проблемы."""

    id: str = Field(description="Идентификатор проблемы")
    name: str = Field(description="Название проблемы")
    target_name: str = Field(alias="targetName")
    count: int = Field(alias="y", description="Количество обращений")

    model_config = {"populate_by_name": True}


class AppealsByProblemResponse(_ListResponse[ProblemAppeal]):
    """Список обращений по типам проблем."""


class AppealDetail(BaseModel):
    """Детальная информация об обращении."""

    id: str = Field(description="Идентификатор обращения")
    agreement_number: str = Field(alias="agreementNumber")
    req_stop: str = Field(alias="reqStop")
    problem_class: str = Field(alias="problemClass")
    group_order: str = Field(alias="groupOrder")
    appeals_count: str = Field(alias="appealsCount")
    group_name: str = Field(alias="groupName")
    address: str
    campus_number: str = Field(alias="campusNumber")
    closed: str
    info: str
    is_error: int = Field(alias="isError")

    model_config = {"populate_by_name": True}


class DetailsByCityResponse(_ListResponse[AppealDetail]):
    """Список детализированных обращений по городу."""


DetailsByProblemResponse = DetailsByCityResponse
