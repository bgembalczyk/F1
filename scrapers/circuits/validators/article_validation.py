from bs4 import BeautifulSoup

CIRCUIT_KEYWORDS = [
    "circuit",
    "race track",
    "racetrack",
    "speedway",
    "raceway",
    "motor racing",
    "motorsport venue",
]


def is_circuit_like_article(soup: BeautifulSoup) -> bool:
    """Sprawdza, czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
    cat_div = soup.find("div", id="mw-normal-catlinks")
    if not cat_div:
        return False

    for a in cat_div.find_all("a"):
        text = a.get_text(strip=True).lower()
        if any(kw in text for kw in CIRCUIT_KEYWORDS):
            return True
    return False
