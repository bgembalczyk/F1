from bs4 import BeautifulSoup

from scrapers.base.helpers.sections import has_category_keyword
from scrapers.circuits.helpers.constants import CIRCUIT_KEYWORDS


def is_circuit_like_article(soup: BeautifulSoup) -> bool:
    """Sprawdza po kategoriach, czy artykuł wygląda na tor (BeautifulSoup -> bool)."""
    return has_category_keyword(soup, CIRCUIT_KEYWORDS)
