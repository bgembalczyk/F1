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

InfoboxPayload = dict[str, Any]
InfoboxRecord = dict[str, Any]

ClassificationT = TypeVar("ClassificationT")
PipelineT = TypeVar("PipelineT")


class SectionInfoboxesHtmlParserABC(HtmlSoupParserABC[list[InfoboxPayload]], ABC):
    """HTML parser section layer: BeautifulSoup -> infobox payloads."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[InfoboxPayload]: ...


class SectionInfoboxClassifierABC(
    ClassifierABC[InfoboxPayload, ClassificationT],
    ABC,
    Generic[ClassificationT],
):
    """Optional classifier for infobox payloads."""

    @abstractmethod
    def classify(self, infobox_data: InfoboxPayload) -> ClassificationT | None: ...


class SectionInfoboxRecordMapperABC(
    MapperABC[InfoboxPayload, InfoboxRecord | None],
    ABC,
    Generic[ClassificationT, PipelineT],
):
    """Mapper from parsed infobox payload + classification into domain record."""

    @abstractmethod
    def map(
        self,
        raw: InfoboxPayload,
        *,
        infobox_classification: ClassificationT,
        infobox_pipeline: PipelineT,
    ) -> InfoboxRecord | None: ...


__all__ = [
    "SectionInfoboxClassifierABC",
    "SectionInfoboxRecordMapperABC",
    "SectionInfoboxesHtmlParserABC",
]
