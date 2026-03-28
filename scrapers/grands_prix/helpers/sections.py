from bs4 import BeautifulSoup

from scrapers.base.helpers.sections import has_category_keyword
from scrapers.base.helpers.sections import has_navbox_template_link
from scrapers.grands_prix.helpers.constants import GRAND_PRIX_KEYWORD
from scrapers.grands_prix.helpers.constants import GRAND_PRIX_NAVBOX_TEMPLATE


def has_grand_prix_navbox(soup: BeautifulSoup) -> bool:
    """Sprawdza navbox Grand Prix po linku szablonu (BeautifulSoup -> bool)."""
    return has_navbox_template_link(soup, GRAND_PRIX_NAVBOX_TEMPLATE)


def has_grand_prix_category(soup: BeautifulSoup) -> bool:
    """Sprawdza kategorię Grand Prix po słowie kluczowym (BeautifulSoup -> bool)."""
    return has_category_keyword(soup, [GRAND_PRIX_KEYWORD])


def is_grand_prix_article(soup: BeautifulSoup) -> bool:
    """Sprawdza, czy artykuł wygląda na Grand Prix (BeautifulSoup -> bool)."""
    return has_grand_prix_navbox(soup) or has_grand_prix_category(soup)
