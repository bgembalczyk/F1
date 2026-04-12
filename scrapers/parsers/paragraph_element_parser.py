from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.base_html_element_parser import BaseHtmlElementParser
from scrapers.parsers.element_parser_abc import ParagraphElementParserABC
from scrapers.text_cleaning import extract_text


class ParagraphElementParser(
    BaseHtmlElementParser[ParagraphElementData],
    ParagraphElementParserABC[ParagraphElementData],
):
    def parse(self, raw: Tag) -> ParagraphElementData:
        return {"text": extract_text(raw) or ""}
