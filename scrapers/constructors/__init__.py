from . import constructors_2025_list as F1_constructors_2025_list_scraper
from . import former_constructors_list as F1_former_constructors_list_scraper
from . import (
    indianapolis_only_constructors_list as F1_indianapolis_only_constructors_list_scraper,
)
from . import privateer_teams_list as F1_privateer_teams_list_scraper
from .constructors_2025_list import Constructors2025ListScraper
from .former_constructors_list import FormerConstructorsListScraper
from .indianapolis_only_constructors_list import IndianapolisOnlyConstructorsListScraper
from .privateer_teams_list import PrivateerTeamsListScraper

F1Constructors2025ListScraper = Constructors2025ListScraper
F1FormerConstructorsListScraper = FormerConstructorsListScraper
F1IndianapolisOnlyConstructorsListScraper = IndianapolisOnlyConstructorsListScraper
F1PrivateerTeamsListScraper = PrivateerTeamsListScraper

__all__ = [
    "Constructors2025ListScraper",
    "FormerConstructorsListScraper",
    "IndianapolisOnlyConstructorsListScraper",
    "PrivateerTeamsListScraper",
    "F1Constructors2025ListScraper",
    "F1FormerConstructorsListScraper",
    "F1IndianapolisOnlyConstructorsListScraper",
    "F1PrivateerTeamsListScraper",
    "F1_constructors_2025_list_scraper",
    "F1_former_constructors_list_scraper",
    "F1_indianapolis_only_constructors_list_scraper",
    "F1_privateer_teams_list_scraper",
]
