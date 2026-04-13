from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.text_cleaning import extract_text


class ParagraphElementParser(HtmlTagParserABC[ParagraphElementData]):
    def parse(self, raw: Tag) -> ParagraphElementData:
        return {"text": extract_text(raw) or ""}
