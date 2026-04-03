from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from bs4 import Tag


def test_wiki_parser_typing_contracts() -> None:
    """Runtime no-op; typing assertions are validated by mypy/pyright."""
    assert True


if TYPE_CHECKING:
    from scrapers.wiki.parsers.base import WikiParser
    from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
    from scrapers.wiki.parsers.elements.table import TableParser
    from scrapers.wiki.parsers.header import HeaderParser
    from scrapers.wiki.parsers.sections.sub_sub_sub_section import (
        SubSubSubSectionParser,
    )
    from scrapers.wiki.parsers.types import HeaderParsedData
    from scrapers.wiki.parsers.types import ParagraphParsedData
    from scrapers.wiki.parsers.types import TableParsedData
    from scrapers.wiki.parsers.types import WikiParsedPayload

    header_parser: WikiParser[HeaderParsedData] = HeaderParser()
    header_result: HeaderParsedData = header_parser.parse(cast(Tag, object()))
    header_title: str | None = header_result["title"]

    paragraph_parser: WikiParser[ParagraphParsedData] = ParagraphParser()
    paragraph_result: ParagraphParsedData = paragraph_parser.parse(cast(Tag, object()))
    paragraph_text: str = paragraph_result["text"]

    table_parser: WikiParser[TableParsedData] = TableParser()
    table_result: TableParsedData = table_parser.parse(cast(Tag, object()))
    table_headers: list[str] = table_result["headers"]

    sub_sub_sub_result = SubSubSubSectionParser().parse(cast(Tag, object()))
    element_payloads: list[WikiParsedPayload] = sub_sub_sub_result["elements"]
