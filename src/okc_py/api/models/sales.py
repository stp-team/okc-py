"""Models for sales API responses."""

from pydantic import BaseModel, Field


class FilterOption(BaseModel):
    """Generic filter option."""

    id: int | str = Field(alias="id", description="Идентификатор опции")
    name: str = Field(alias="name", description="Название опции")


class HeadFilterOption(BaseModel):
    """Head filter option for date-based queries."""

    id: int = Field(alias="id", description="ID руководителя")
    name: str = Field(alias="name", description="ФИО руководителя")
    subdivision_id: int = Field(alias="subdivisionId", description="ID подразделения")
    unit_id: int = Field(alias="unitId", description="ID направления")


class EmployeeFilterOption(BaseModel):
    """Employee filter option for date-based queries."""

    id: int = Field(alias="id", description="ID сотрудника")
    name: str = Field(alias="name", description="ФИО сотрудника")
    head_id: int = Field(alias="headId", description="ID руководителя")
    unit_id: int = Field(alias="unitId", description="ID направления")
    subdivision_id: int = Field(alias="subdivisionId", description="ID подразделения")
    active_to: str = Field(alias="activeTo", description="Активен до")


class SubdivisionFilterOption(FilterOption):
    """Subdivision filter option with associated units."""

    units: list[int] = Field(alias="units", description="Связанные направления")


class SalesFilters(BaseModel):
    """Available filters for sales report."""

    units: list[FilterOption] = Field(
        alias="units", description="Доступные направления"
    )
    subdivisions: list[SubdivisionFilterOption] = Field(
        alias="subdivisions", description="Доступные подразделения"
    )
    materials_ens_segments: list[FilterOption] = Field(
        alias="materialsEnsSegments", description="Сегменты оборудования"
    )
    sales_types: list[FilterOption] = Field(
        alias="salesTypes", description="Доступные типы продаж"
    )


class SalesFiltersByDate(BaseModel):
    """Available filters for sales report by date range."""

    heads: list[HeadFilterOption] = Field(
        alias="heads", description="Доступные руководители"
    )
    employees: list[EmployeeFilterOption] = Field(
        alias="employees", description="Доступные сотрудники"
    )


class SalesReportHeader(BaseModel):
    """Column header definition for sales report."""

    title: str = Field(alias="title", description="Заголовок колонки")
    key: str = Field(alias="key", description="Ключ поля данных")


class SalesReportRow(BaseModel):
    """Single row in sales report data."""

    fullname: str = Field(alias="fio", description="ФИО продавца")
    unit_name: str = Field(alias="unitName", description="Название направления")
    subdivision_name: str = Field(
        alias="subdivisionName", description="Название подразделения"
    )
    post_name: str = Field(alias="postName", description="Должность")
    head_fio: str = Field(alias="headFio", description="ФИО руководителя")
    sale_date: str = Field(alias="saleDate", description="Дата продажи")
    city_name: str = Field(alias="cityName", description="Город")
    agreement_number: str = Field(alias="agreementNumber", description="Номер договора")
    materials_ens_name: str = Field(
        alias="materialsEnsName", description="Наименование оборудования"
    )
    cost_type: str = Field(alias="costType", description="Тип затрат")
    is_loan: str = Field(alias="isLoan", description="Является ли кредитом")
    segment_name: str = Field(alias="segmentName", description="Сегмент")
    request_id: str = Field(alias="requestId", description="ID заявки")
    proc_name: str = Field(alias="procName", description="Бизнес-процесс")
    base_cost: str = Field(alias="baseCost", description="Базовая стоимость")


class SalesReport(BaseModel):
    """Sales report response."""

    headers: list[SalesReportHeader] = Field(
        alias="headers", description="Заголовки колонок отчёта"
    )
    data: list[SalesReportRow] = Field(alias="data", description="Данные отчёта")
