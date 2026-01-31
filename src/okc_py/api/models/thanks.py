"""Data models for thanks (благодарности) API."""

from pydantic import BaseModel, Field


class ThanksReportRequest(BaseModel):
    """Request model for thanks report filters."""

    whom_units: list[int] = Field(default_factory=list, alias="whomUnits")
    whom_subdivisions: list[int] = Field(default_factory=list, alias="whomSubdivisions")
    whom_heads: list[int] = Field(default_factory=list, alias="whomHeads")
    whom_employees: list[int] = Field(default_factory=list, alias="whomEmployees")
    start_date: str | None = Field(None, alias="startDate")
    stop_date: str | None = Field(None, alias="stopDate")
    init_units: list[int] = Field(default_factory=list, alias="initUnits")
    init_subdivisions: list[int] = Field(default_factory=list, alias="initSubdivisions")
    who_processed: list[int] = Field(default_factory=list, alias="whoProcessed")
    agreement: str | None = Field(None, alias="agreement")
    statuses: list[int] = Field(default_factory=list, alias="statuses")


class ThanksReportItem(BaseModel):
    """Single thanks report entry."""

    id: str = Field(..., alias="id")
    rn: int = Field(..., alias="rn")
    thanks_appl_id: int = Field(..., alias="thanksApplId")
    processed_id: int = Field(..., alias="processedId")
    appl_date: str = Field(..., alias="applDate")
    initiator_name: str = Field(..., alias="initiatorName")
    init_subdivision: str = Field(..., alias="initSubdivision")
    agreement_number: str | None = Field(None, alias="agreementNumber")
    rckd: str | None = Field(None, alias="rckd")
    rck: str | None = Field(None, alias="rck")
    interaction_id: str | None = Field(None, alias="interactionId")
    info: str = Field(..., alias="info")
    class3_name: str = Field(..., alias="class3Name")
    status_id: int = Field(..., alias="statusId")
    status_name: str = Field(..., alias="statusName")
    processed_comment: str | None = Field(None, alias="processedComment")
    processed_date: str | None = Field(None, alias="processedDate")
    whom_id: int = Field(..., alias="whomId")
    whom_name: str = Field(..., alias="whomName")
    whom_head_name: str = Field(..., alias="whomHeadName")
    whom_subdivision: str = Field(..., alias="whomSubdivision")
    whom_unit: str = Field(..., alias="whomUnit")
    who_name: str = Field(..., alias="whoName")
    doubles_count: int = Field(..., alias="doublesCount")


class ThanksReportResponse(BaseModel):
    """Response model for thanks report."""

    items: list[ThanksReportItem] = Field(default_factory=list)

    @classmethod
    def model_validate(
        cls,
        obj,
        *,
        strict=None,
        extra=None,
        from_attributes=None,
        context=None,
        by_alias=None,
        by_name=None,
    ):
        """Validate from API response data."""
        if isinstance(obj, list):
            return cls(items=[ThanksReportItem.model_validate(item) for item in obj])
        elif isinstance(obj, dict) and "items" in obj:
            return cls(
                items=[ThanksReportItem.model_validate(item) for item in obj["items"]]
            )
        else:
            return cls(items=[])
