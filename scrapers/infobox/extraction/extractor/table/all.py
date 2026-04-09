from bs4 import BeautifulSoup
from bs4 import Tag


class AllInfoboxTablesExtractor:
    """Helper strategii zwracający wszystkie HTML-owe tabele infobox."""

    @staticmethod
    def find_infoboxes(soup: BeautifulSoup) -> list[Tag]:
        return [
            table
            for table in soup.find_all("table", class_="infobox")
            if isinstance(table, Tag)
        ]
