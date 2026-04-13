from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.parsers.contracts.classifier_abc import ClassifierABC
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC

TablePayload = dict[str, Any]
TableRecord = dict[str, Any]

ClassificationT = TypeVar("ClassificationT")


class SectionTablesHtmlParserABC(HtmlSoupParserABC[list[TablePayload]], ABC):
    """Backward-compat alias. Use HtmlSoupParserABC[list[TablePayload]] directly."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[TablePayload]: ...


class SectionTableClassifierABC(
    ClassifierABC[TablePayload, ClassificationT],
    ABC,
    Generic[ClassificationT],
):
    """Klasyfikator payloadu tabeli sekcji."""

    @abstractmethod
    def classify(self, table_data: TablePayload) -> ClassificationT | None: ...
