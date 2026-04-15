from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType
from scrapers.text_cleaning import extract_text


class WikiReferencesElementParser(ParserABC[Tag, ReferencesWrapParsedData]):
    """Wikipedia HTML element parser for references wrappers.

    Przetwarza divy z klasą zawierającą 'references-wrap'.
    """

    element_type: WikiElementType = "references"

    def parse(self, raw: Tag) -> ReferencesWrapParsedData:
        refs = [extract_text(li) or "" for li in raw.find_all("li")]
        return {"references": refs}
