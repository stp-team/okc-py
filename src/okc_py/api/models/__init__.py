"""Data models for OKC API."""

from .dossier import Employee, EmployeeData
from .premium import HeadPremiumResponse, SpecialistPremiumResponse
from .sl import ReportData, SlRootModel
from .tests import AssignedTest
from .thanks import ThanksReportItem, ThanksReportRequest, ThanksReportResponse
from .tutors import GraphFiltersResponse, TutorGraphResponse
from .ure import TypedKPIResponse

__all__ = [
    "AssignedTest",
    "Employee",
    "EmployeeData",
    "GraphFiltersResponse",
    "HeadPremiumResponse",
    "ReportData",
    "SlRootModel",
    "SpecialistPremiumResponse",
    "ThanksReportItem",
    "ThanksReportRequest",
    "ThanksReportResponse",
    "TutorGraphResponse",
    "TypedKPIResponse",
]
