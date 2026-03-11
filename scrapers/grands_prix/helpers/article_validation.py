from bs4 import BeautifulSoup

GRAND_PRIX_KEYWORD = "grand prix"
GRAND_PRIX_NAVBOX_TEMPLATE = "Template:Formula_One_Grands_Prix"


def has_grand_prix_navbox(soup: BeautifulSoup) -> bool:
    navboxes = soup.find_all("table", class_="navbox-inner")
    for navbox in navboxes:
        if navbox.find(
                "a", href=lambda href: href and GRAND_PRIX_NAVBOX_TEMPLATE in href,
        ):
            return True
    return False


def has_grand_prix_category(soup: BeautifulSoup) -> bool:
    cat_div = soup.find("div", id="mw-normal-catlinks")
    if not cat_div:
        return False

    for link in cat_div.find_all("a"):
        text = link.get_text(strip=True).lower()
        if GRAND_PRIX_KEYWORD in text:
            return True
    return False


def is_grand_prix_article(soup: BeautifulSoup) -> bool:
    """Sprawdza, czy artykuł wygląda na Grand Prix (navbox lub kategorie)."""
    if has_grand_prix_navbox(soup):
        return True
    return has_grand_prix_category(soup)
