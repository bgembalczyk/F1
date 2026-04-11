from abc import ABC
from abc import abstractmethod
import warnings
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser
from scrapers.parsers.input_types import WikiDictFragmentInput

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


class WikiTableElementParserBase(WikiParser[BeautifulSoup, WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""


class WikiTableParser(WikiTableElementParserBase, ABC):
    """Deprecated alias for :class:`WikiTableElementParserBase`."""

    def __init_subclass__(cls, **kwargs: object) -> None:
        warnings.warn(
            "WikiTableParser is deprecated; use WikiTableElementParserBase.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)


class WikiListParser(WikiParser[Tag, WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""


class WikiTagParser(WikiParser[Tag, TWikiOutput], ABC, Generic[TWikiOutput]):
    """Kontrakt parserów pojedynczych tagów HTML Wikipedii."""


WikiFragmentParser = WikiParser[WikiDictFragmentInput, TWikiOutput]


__all__ = [
    "WikiFragmentParser",
    "WikiListParser",
    "WikiParser",
    "WikiRecord",
    "WikiRecords",
    "WikiSectionParser",
    "WikiTableElementParserBase",
    "WikiTableParser",
    "WikiTagParser",
]
