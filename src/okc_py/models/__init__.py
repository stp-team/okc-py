"""Data models for OKC API."""

from .dossier import Employee, EmployeeData
from .premium import SpecialistPremiumResponse, HeadPremiumResponse
from .ure import TypedKPIResponse
from .sl import ReportData, SlRootModel
from .tutors import TutorGraphResponse, GraphFiltersResponse

__all__ = [
    "Employee",
    "EmployeeData",
    "SpecialistPremiumResponse",
    "HeadPremiumResponse",
    "TypedKPIResponse",
    "ReportData",
    "SlRootModel",
    "TutorGraphResponse",
    "GraphFiltersResponse",
]
