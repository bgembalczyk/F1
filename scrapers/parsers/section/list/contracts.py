from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.mappers.mapper_abc import MapperABC
from scrapers.parsers.contracts.classifier_abc import ClassifierABC
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC

ListPayload = dict[str, Any]
ListRecord = dict[str, Any]

ClassificationT = TypeVar("ClassificationT")
PipelineT = TypeVar("PipelineT")


class SectionListsHtmlParserABC(HtmlSoupParserABC[list[ListPayload]], ABC):
    """HTML parser section layer: BeautifulSoup -> list payloads."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[ListPayload]: ...


class SectionListClassifierABC(ClassifierABC[ListPayload, ClassificationT], ABC, Generic[ClassificationT]):
    """Optional classifier for list payloads extracted from section HTML."""

    @abstractmethod
    def classify(self, list_data: ListPayload) -> ClassificationT | None: ...


class SectionListRecordMapperABC(MapperABC[ListPayload, ListRecord | None], ABC, Generic[ClassificationT, PipelineT]):
    """Mapper from list payload + classification into domain record."""

    @abstractmethod
    def map(
        self,
        raw: ListPayload,
        *,
        list_classification: ClassificationT,
        list_pipeline: PipelineT,
    ) -> ListRecord | None: ...


__all__ = [
    "SectionListClassifierABC",
    "SectionListRecordMapperABC",
    "SectionListsHtmlParserABC",
]
