from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.core.domain_roles import Parser

WikiRecord = dict[str, Any]
WikiRecords = list[WikiRecord]

TWikiInput = TypeVar("TWikiInput")
TWikiOutput = TypeVar("TWikiOutput")


class WikiParser(
    Parser[TWikiInput, TWikiOutput],
    ABC,
    Generic[TWikiInput, TWikiOutput],
):
    """Bazowy kontrakt parserów Wikipedii.

    Każdy parser implementuje jednolity entrypoint `parse(...)` i zwraca
    jawnie typowane dane wyjściowe.
    """

    @abstractmethod
    def parse(self, element: TWikiInput, *args: Any, **kwargs: Any) -> TWikiOutput:
        """Parsuje przekazane dane wejściowe Wikipedii."""


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
