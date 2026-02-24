from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pydantic import ExtraValues


class BasePremiumData(BaseModel):
    """Base class for common premium data fields"""

    # Базовые идентификаторы
    core_id: int = Field(..., alias="CORE_ID")
    person_id: int = Field(..., alias="PERSON_ID")
    employee_id: int = Field(..., alias="EMPLOYEE_ID")
    user_fullname: str | None = Field(None, alias="USER_FIO")
    head_id: int | None = Field(None, alias="HEAD_ID")
    head_fullname: str | None = Field(None, alias="HEAD_FIO")
    period: str = Field(..., alias="PERIOD")

    # Организация
    subdivision_id: int = Field(..., alias="SUBDIVISION_ID")
    subdivision_name: str = Field(..., alias="SUBDIVISION_NAME")
    post_id: int = Field(..., alias="POST_ID")
    post_name: str = Field(..., alias="POST_NAME")
    user_type_id: int = Field(..., alias="USER_TYPE_ID")
    user_type_description: str = Field(..., alias="USER_TYPE_DESCRIPTION")

    # ГОК
    gok: float = Field(..., alias="GOK")
    gok_normative: float | None = Field(None, alias="GOK_NORMATIVE")
    gok_pers_normative: float | None = Field(None, alias="PERS_GOK_NORMATIVE")
    gok_normative_rate: float | None = Field(None, alias="NORM_GOK")
    gok_renormative_rate: float | None = Field(None, alias="RENORM_GOK")
    gok_weight: float | None = Field(None, alias="GOK_WEIGHT")
    gok_premium: float = Field(..., alias="PERC_GOK")

    # Спец. цель
    pers_target_type_id: int | None = Field(None, alias="PERS_TARGET_TYPE_ID")
    target: float | None = Field(None, alias="PERS_FACT")
    target_type: str | None = Field(None, alias="PERS_TARGET_TYPE_NAME")
    target_normative_first: float | None = Field(None, alias="PERS_PLAN_1")
    target_normative_second: float | None = Field(None, alias="PERS_PLAN_2")
    target_normative_rate_first: float | None = Field(None, alias="PERS_RESULT_1")
    target_normative_rate_second: float | None = Field(None, alias="PERS_RESULT_2")
    target_premium: int | None = Field(None, alias="PERS_PERCENT")
    pers_target_manual: int | None = Field(None, alias="PERS_TARGET_MANUAL")

    # Результаты
    head_adjust_premium: float | None = Field(None, alias="HEAD_ADJUST")
    total_premium: float = Field(..., alias="TOTAL_PREMIUM")
    commentary: str | None = Field(None, alias="COMMENTARY")


class SpecialistPremiumData(BasePremiumData):
    """Model for specialist premium data"""

    # CSAT (Customer Satisfaction)
    csat: float | None = Field(None, alias="CSAT")
    csat_normative: float | None = Field(None, alias="CSAT_NORMATIVE")
    csat_pers_normative: float | None = Field(None, alias="PERS_CSAT_NORMATIVE")
    csat_normative_rate: float | None = Field(None, alias="NORM_CSAT")
    csat_renormative_rate: float | None = Field(None, alias="RENORM_CSAT")
    csat_weight: float | None = Field(None, alias="CSAT_WEIGHT")
    csat_premium: float | None = Field(None, alias="PERC_CSAT")

    # CSI Response
    csi_response: float | None = Field(None, alias="CSI_RESPONSE")
    csi_response_normative: float | None = Field(None, alias="CSI_RESPONSE_NORMATIVE")
    csi_response_normative_rate: float | None = Field(None, alias="NORM_CSI_RESPONSE")

    # AHT (Average Handle Time)
    aht: float | None = Field(None, alias="AHT")
    aht_normative: float | None = Field(None, alias="AHT_NORMATIVE")
    aht_pers_normative: float | None = Field(None, alias="PERS_AHT_NORMATIVE")
    aht_normative_rate: float | None = Field(None, alias="NORM_AHT")
    aht_renormative_rate: float | None = Field(None, alias="RENORM_AHT")
    aht_weight: float | None = Field(None, alias="AHT_WEIGHT")
    aht_premium: float | None = Field(None, alias="PERC_AHT")

    # Специфичные для специалистов поля
    total_chats: int | None = Field(None, alias="TOTAL_CHATS")
    raw_premium: float | None = Field(None, alias="RAW_PREMIUM")


class HeadPremiumData(BasePremiumData):
    """Model for head (supervisor) premium data"""

    # FLR (First Line Resolution)
    flr: float | None = Field(None, alias="FLR")
    flr_normative: float | None = Field(None, alias="FLR_NORMATIVE")
    flr_pers_normative: float | None = Field(None, alias="PERS_FLR_NORMATIVE")
    flr_normative_rate: float | None = Field(None, alias="NORM_FLR")
    flr_renormative_rate: float | None = Field(None, alias="RENORM_FLR")
    flr_weight: float | None = Field(None, alias="FLR_WEIGHT")
    flr_premium: float | None = Field(None, alias="PERC_FLR")

    # AHT (Average Handle Time)
    aht: float | None = Field(None, alias="AHT")
    aht_normative: float | None = Field(None, alias="AHT_NORMATIVE")
    aht_pers_normative: float | None = Field(None, alias="PERS_AHT_NORMATIVE")
    aht_normative_rate: float | None = Field(None, alias="NORM_AHT")
    aht_renormative_rate: float | None = Field(None, alias="RENORM_AHT")
    aht_weight: float | None = Field(None, alias="AHT_WEIGHT")
    aht_premium: float | None = Field(None, alias="PERC_AHT")

    # Специфичные для руководителей поля
    raw_premium: float | None = Field(None, alias="RAW_PREMIUM")


class HeadPremiumResponse(BaseModel):
    """Wrapper for head premium response with not eligible employees"""

    premium: list[HeadPremiumData] = Field(...)
    not_eligible: dict[str, list[str]] = Field(..., alias="notEligible")


class SpecialistPremiumResponse(BaseModel):
    """Response model for specialist premium data"""

    items: list[SpecialistPremiumData] = Field(...)

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: "ExtraValues | None" = None,  # type: ignore[valid-type]
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ):
        """Validate from API response data"""
        if isinstance(obj, list):
            # If data is a list, wrap it in the items field
            return cls(
                items=[SpecialistPremiumData.model_validate(item) for item in obj]
            )
        elif isinstance(obj, dict) and "items" in obj:
            # If data already has items field
            return super().model_validate(
                obj,
                strict=strict,
                extra=extra,
                from_attributes=from_attributes,
                context=context,
                by_alias=by_alias,
                by_name=by_name,
            )
        else:
            # Fallback to standard validation
            return super().model_validate(
                obj,
                strict=strict,
                extra=extra,
                from_attributes=from_attributes,
                context=context,
                by_alias=by_alias,
                by_name=by_name,
            )
