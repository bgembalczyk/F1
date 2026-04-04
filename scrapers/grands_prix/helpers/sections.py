from bs4 import BeautifulSoup

from scrapers.base.helpers.sections import has_category_keyword
from scrapers.base.helpers.sections import has_navbox_template_link
from scrapers.grands_prix.helpers.constants import GRAND_PRIX_KEYWORD
from scrapers.grands_prix.helpers.constants import GRAND_PRIX_NAVBOX_TEMPLATE


def is_grand_prix_article(soup: BeautifulSoup) -> bool:
    """Sprawdza, czy artykuł wygląda na Grand Prix (BeautifulSoup -> bool)."""
    has_navbox = has_navbox_template_link(soup, GRAND_PRIX_NAVBOX_TEMPLATE)
    has_category = has_category_keyword(soup, [GRAND_PRIX_KEYWORD])
    return has_navbox or has_category
