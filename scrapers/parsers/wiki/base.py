from abc import ABC
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser
from scrapers.parsers.input_types import WikiDictFragmentInput
from scrapers.parsers.roles import HtmlTagParserABC
from scrapers.parsers.roles import SoupDocumentParserABC

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


class WikiSectionParserBase(SoupDocumentParserABC[WikiRecords], ABC):
    """Kontrakt parserów sekcji artykułów Wikipedii."""


class WikiTableElementParserBase(SoupDocumentParserABC[WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""


class WikiListParser(HtmlTagParserABC[Tag, WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""


class WikiTagParser(HtmlTagParserABC[Tag, TWikiOutput], ABC, Generic[TWikiOutput]):
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
