from bs4 import Tag

from models.data.parsed.html_elements import ListElementData
from scrapers.parsers.html_elements.base import BaseHtmlElementParser
from scrapers.parsers.text_cleaning import extract_text


class ListElementParser(BaseHtmlElementParser[ListElementData]):
    def parse(self, element: Tag) -> ListElementData:
        return {
            "items": [extract_text(li) or "" for li in element.find_all("li", recursive=False)],
        }
