from abc import ABC
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.input_types import WikiDictFragmentInput
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.soup_parser_abc import HtmlSoupParserABC
from scrapers.parsers.tag_parser_abc import HtmlTagParserABC

WikiRecord = dict[str, Any]
WikiRecords = list[WikiRecord]

TWikiInput = TypeVar("TWikiInput")
TWikiOutput = TypeVar("TWikiOutput")


class WikiParser(
    ParserABC[TWikiInput, TWikiOutput],
    ABC,
    Generic[TWikiInput, TWikiOutput],
):
    """Bazowy kontrakt parserów Wikipedii oparty o kanoniczny `Parser`.

    Implementacje dostarczają `parse(input) -> output` z jawnie typowanym
    wejściem i wyjściem.
    """












__all__ = [
    "WikiParser",
    "WikiRecord",
    "WikiRecords",
]
