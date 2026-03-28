from collections.abc import Iterable

from bs4 import BeautifulSoup


def get_category_texts(soup: BeautifulSoup) -> list[str]:
    """Pobiera teksty kategorii z `mw-normal-catlinks` (BeautifulSoup -> list[str])."""
    cat_div = soup.find("div", id="mw-normal-catlinks")
    if not cat_div:
        return []

    return [link.get_text(strip=True).lower() for link in cat_div.find_all("a")]


def has_category_keyword(soup: BeautifulSoup, keywords: Iterable[str]) -> bool:
    """Sprawdza słowa kluczowe w kategoriach (BeautifulSoup -> bool)."""
    category_texts = get_category_texts(soup)
    return any(keyword in text for text in category_texts for keyword in keywords)


def has_navbox_template_link(soup: BeautifulSoup, template_href_fragment: str) -> bool:
    """Opcjonalnie sprawdza navboxy po wzorcu linku (BeautifulSoup -> bool)."""
    navboxes = soup.find_all("table", class_="navbox-inner")
    for navbox in navboxes:
        if navbox.find(
            "a",
            href=lambda href: href and template_href_fragment in href,
        ):
            return True
    return False
