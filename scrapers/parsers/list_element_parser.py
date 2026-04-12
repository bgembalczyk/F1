from bs4 import Tag

from models.data.parsed.html_elements import ListElementData
from scrapers.parsers.wiki.section_nodes.list import WikiListParserABC
from scrapers.text_cleaning import extract_text


class ListElementParser(WikiListParserABC):
    def parse(self, raw: Tag) -> ListElementData:
        return {
            "items": [extract_text(li) or "" for li in raw.find_all("li", recursive=False)],
        }
