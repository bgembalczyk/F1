from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from models.payload import WikiParsedPayload
from scrapers.mapper_abc import MapperABC

RawPayloadT = TypeVar("RawPayloadT")
ClassificationT = TypeVar("ClassificationT")


class WikiElementClassifierABC(ABC, Generic[RawPayloadT, ClassificationT]):
    """Optional classifier stage used between HTML parser and payload mapper."""

    @abstractmethod
    def classify(self, raw: RawPayloadT) -> ClassificationT | None: ...


class WikiElementPayloadMapperABC(
    MapperABC[RawPayloadT, WikiParsedPayload],
    ABC,
    Generic[RawPayloadT, ClassificationT],
):
    """Mapper stage translating element payload + classification into parsed record."""

    @abstractmethod
    def map(
        self,
        raw: RawPayloadT,
        *,
        element_type: str,
        section_id: str | None,
        classification: ClassificationT,
        raw_html_fragment: str,
        confidence: float,
    ) -> WikiParsedPayload: ...


class WikiDomainMapperABC(MapperABC[dict[str, Any], dict[str, Any]], ABC):
    """Parser/domain boundary mapper for section output payloads."""

    @abstractmethod
    def map(self, raw: dict[str, Any]) -> dict[str, Any]: ...


__all__ = [
    "ClassificationT",
    "RawPayloadT",
    "WikiDomainMapperABC",
    "WikiElementClassifierABC",
    "WikiElementPayloadMapperABC",
]
