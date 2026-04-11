from abc import ABC
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser

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


class WikiSectionParser(WikiParser[BeautifulSoup, WikiRecords], ABC):
    """Kontrakt parserów sekcji artykułów Wikipedii."""


class WikiTableParser(WikiParser[BeautifulSoup, WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""


class WikiListParser(WikiParser[Tag, WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""


class WikiTagParser(WikiParser[Tag, TWikiOutput], ABC, Generic[TWikiOutput]):
    """Kontrakt parserów pojedynczych tagów HTML Wikipedii."""


__all__ = [
    "WikiListParser",
    "WikiParser",
    "WikiRecord",
    "WikiRecords",
    "WikiSectionParser",
    "WikiTableParser",
    "WikiTagParser",
]
