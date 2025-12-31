"""Repository modules for OKC API."""

from .dossier import DossierAPI
from .premium import PremiumAPI
from .sl import SlAPI
from .tutors import TutorsAPI
from .ure import UreAPI

__all__ = ["DossierAPI", "PremiumAPI", "UreAPI", "SlAPI", "TutorsAPI"]
