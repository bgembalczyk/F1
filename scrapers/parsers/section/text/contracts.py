from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.mapper_abc import MapperABC
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC

TextSectionPayload = dict[str, Any]
TextSectionRecord = dict[str, Any]

ClassificationT = TypeVar("ClassificationT")
PipelineT = TypeVar("PipelineT")


class SectionTextBlocksHtmlParserABC(HtmlSoupParserABC[list[TextSectionPayload]], ABC):
    """HTML parser section layer: BeautifulSoup -> text-block payloads."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[TextSectionPayload]: ...


class SectionTextClassifierABC(ABC, Generic[ClassificationT]):
    """Optional classifier for parsed section text payload."""

    @abstractmethod
    def classify(self, text_data: TextSectionPayload) -> ClassificationT | None: ...


class SectionTextRecordMapperABC(MapperABC[TextSectionPayload, TextSectionRecord | None], ABC, Generic[ClassificationT, PipelineT]):
    """Mapper from parsed text payload + classification into domain record."""

    @abstractmethod
    def map(
        self,
        raw: TextSectionPayload,
        *,
        text_classification: ClassificationT,
        text_pipeline: PipelineT,
    ) -> TextSectionRecord | None: ...


__all__ = [
    "SectionTextBlocksHtmlParserABC",
    "SectionTextClassifierABC",
    "SectionTextRecordMapperABC",
]
