"""API repository modules for OKC."""

from okc_py.api.repos.appeals import AppealsAPI
from okc_py.api.repos.dossier import DossierAPI
from okc_py.api.repos.incidents import IncidentsAPI
from okc_py.api.repos.lines import LinesAPI
from okc_py.api.repos.premium import PremiumAPI
from okc_py.api.repos.sales import SalesAPI
from okc_py.api.repos.sl import SlAPI
from okc_py.api.repos.tests import TestsAPI
from okc_py.api.repos.tutors import TutorsAPI
from okc_py.api.repos.ure import UreAPI

__all__ = [
    "DossierAPI",
    "PremiumAPI",
    "SlAPI",
    "TestsAPI",
    "TutorsAPI",
    "UreAPI",
    "AppealsAPI",
    "IncidentsAPI",
    "LinesAPI",
    "SalesAPI",
]
