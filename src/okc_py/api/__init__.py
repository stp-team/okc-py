"""API repository modules for OKC."""

from .repos.appeals import AppealsAPI
from .repos.dossier import DossierAPI
from .repos.incidents import IncidentsAPI
from .repos.lines import LinesAPI
from .repos.premium import PremiumAPI
from .repos.sales import SalesAPI
from .repos.sl import SlAPI
from .repos.tests import TestsAPI
from .repos.tutors import TutorsAPI
from .repos.ure import UreAPI

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
