from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.mapper_abc import MapperABC
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC

TablePayload = dict[str, Any]
TableRecord = dict[str, Any]

ClassificationT = TypeVar("ClassificationT")
PipelineT = TypeVar("PipelineT")


class SectionTablesHtmlParserABC(HtmlSoupParserABC[list[TablePayload]], ABC):
    """HTML parser warstwy sekcji: BeautifulSoup -> lista payloadów tabel."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[TablePayload]: ...


class SectionTableClassifierABC(ABC, Generic[ClassificationT]):
    """Klasyfikator payloadu tabeli sekcji."""

    @abstractmethod
    def classify(self, table_data: TablePayload) -> ClassificationT | None: ...


class SectionTableRecordMapperABC(MapperABC[TablePayload, TableRecord | None], ABC, Generic[ClassificationT, PipelineT]):
    """Mapper payloadu tabeli + klasyfikacji na rekord domenowy sekcji."""

    @abstractmethod
    def map(
        self,
        raw: TablePayload,
        *,
        table_classification: ClassificationT,
        table_pipeline: PipelineT,
    ) -> TableRecord | None: ...
