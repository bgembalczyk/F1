from bs4 import BeautifulSoup
from bs4 import Tag


class FirstInfoboxTableExtractor:
    """Helper strategii zwracający pierwszy HTML-owy infobox tabelaryczny."""

    @staticmethod
    def find_infoboxes(soup: BeautifulSoup) -> list[Tag]:
        table = soup.find("table", class_="infobox")
        return [table] if isinstance(table, Tag) else []
