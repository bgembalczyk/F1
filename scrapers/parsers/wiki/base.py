from abc import ABC
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.contracts.parser_abc import ParserABC as Parser
from scrapers.parsers.input_types import WikiDictFragmentInput
from scrapers.parsers.contracts.soup_parser_abc import TagParserABC
from scrapers.parsers.contracts.soup_parser_abc import SoupParserABC

WikiRecord = dict[str, Any]
WikiRecords = list[WikiRecord]

TWikiInput = TypeVar("TWikiInput")
TWikiOutput = TypeVar("TWikiOutput")


class WikiParser(
    Parser[TWikiInput, TWikiOutput],
    ABC,
    Generic[TWikiInput, TWikiOutput],
):
    """Bazowy kontrakt parserów Wikipedii oparty o kanoniczny `Parser`.

    Implementacje dostarczają `parse(input) -> output` z jawnie typowanym
    wejściem i wyjściem.
    """


class WikiSectionParserBase(SoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów sekcji artykułów Wikipedii."""


class WikiTableElementParserBase(SoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""


class WikiListParser(TagParserABC[WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""


class WikiTagParser(TagParserABC[TWikiOutput], ABC, Generic[TWikiOutput]):
    """Kontrakt parserów pojedynczych tagów HTML Wikipedii."""


WikiFragmentParser = WikiParser[WikiDictFragmentInput, TWikiOutput]


__all__ = [
    "WikiFragmentParser",
    "WikiListParser",
    "WikiParser",
    "WikiRecord",
    "WikiRecords",
    "WikiSectionParserBase",
    "WikiTableElementParserBase",
    "WikiTagParser",
]
