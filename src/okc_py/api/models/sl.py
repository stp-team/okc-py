from typing import Any

from pydantic import BaseModel, Field, field_validator


class QueueItem(BaseModel):
    title: str
    vqList: list[str]


class NtpNck(BaseModel):
    title: str
    unitId: int
    queues: list[QueueItem]


class SlRootModel(BaseModel):
    ntp_nck: NtpNck


class TotalData(BaseModel):
    total_entered: float = Field(alias="Поступило", description="Поступило чатов")
    total_answered: float = Field(alias="Принято", description="Принято чатов")
    total_abandoned: float = Field(alias="Пропущено", description="Пропущено чатов")
    answered_in_sl: float = Field(alias="Принято в SL", description="Принято в SL")
    answered_percent: float = Field(alias="% Принятых", description="% принятых чатов")


class DetailHeader(BaseModel):
    title: str
    key: str


class DetailRow(BaseModel):
    half_hour_text: str = Field(alias="HALF_HOUR_TEXT", description="Период")
    total_entered: int = Field(alias="TOTAL_ENTERED", description="Поступившие чаты")
    total_answered: int = Field(alias="TOTAL_ANSWERED", description="Принятые чаты")
    total_abandoned: int = Field(
        alias="TOTAL_ABANDONED", description="Пропущенные чаты"
    )
    total_to_nck_tech: int = Field(
        alias="TOTAL_TO_NCK_TECH", description="Переливы в НЦКТех"
    )
    average_release_time: int | None = Field(
        None, alias="AVERAGE_RELEASE_TIME", description="Среднее время обработки чатов"
    )
    average_answer_time: int | None = Field(
        None, alias="AVERAGE_ANSWER_TIME", description="Среднее время ожидания ответа"
    )
    sl: float | None = Field(None, alias="SL", description="Service level")


class DetailData(BaseModel):
    headers: list[DetailHeader]
    data: list[DetailRow]


class ReportData(BaseModel):
    total_data: TotalData = Field(alias="totalData")
    detail_data: DetailData = Field(alias="detailData")

    @field_validator("total_data", mode="before")
    @classmethod
    def transform_total_data(cls, v: list[dict]) -> dict[Any, Any] | list[dict]:
        """Transform list of text/value pairs into proper object."""
        if isinstance(v, list):
            return {item["text"]: item["value"] for item in v}
        return v
