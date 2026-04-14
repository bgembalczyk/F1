from bs4 import Tag

from models.data.parsed.html_elements import ListElementData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType
from scrapers.text_cleaning import extract_text


class ListElementParser(HtmlTagParserABC[ListElementData]):
    element_type: WikiElementType = "list"

    def parse(self, raw: Tag) -> ListElementData:
        return {
            "items": [
                extract_text(li) or "" for li in raw.find_all("li", recursive=False)
            ],
        }
