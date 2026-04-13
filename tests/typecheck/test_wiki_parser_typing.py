from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from scrapers.parsers.wiki.sub_sub_sub_section import SubSubSubSectionParser


def test_wiki_parser_typing_contracts() -> None:
    """Runtime no-op; typing assertions are validated by mypy/pyright."""
    assert True


if TYPE_CHECKING:
    from bs4 import Tag

    from models.data.parsed.header import HeaderParsedData
    from models.data.parsed.paragraph import ParagraphParsedData
    from models.data.parsed.table import TableParsedData
    from models.payload import WikiParsedPayload
    from scrapers.parsers.parser_abc import ParserABC
    from scrapers.parsers.wiki.header import HeaderParser
    from scrapers.parsers.wiki.paragraph import WikiParagraphParser
    from scrapers.parsers.wiki.table import WikiTableParser

    header_parser: ParserABC[Tag, HeaderParsedData] = HeaderParser()
    header_result: HeaderParsedData = header_parser.parse(cast("Tag", object()))
    header_title: str | None = header_result["title"]

    paragraph_parser: ParserABC[Tag, ParagraphParsedData] = WikiParagraphParser()
    paragraph_result: ParagraphParsedData = paragraph_parser.parse(
        cast("Tag", object()),
    )
    paragraph_text: str = paragraph_result["text"]

    table_parser: ParserABC[Tag, TableParsedData] = WikiTableParser()
    table_result: TableParsedData = table_parser.parse(cast("Tag", object()))
    table_headers: list[str] = table_result["headers"]

    sub_sub_sub_result = SubSubSubSectionParser().parse(cast("Tag", object()))
    element_payloads: list[WikiParsedPayload] = sub_sub_sub_result["elements"]
