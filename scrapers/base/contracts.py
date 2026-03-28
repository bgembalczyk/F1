from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

PayloadT = TypeVar("PayloadT", contravariant=True)
SectionOutputT = TypeVar("SectionOutputT", covariant=True)
RecordT = TypeVar("RecordT", covariant=True)


class SectionService(Protocol[SectionOutputT]):
    """Contract for domain section extraction services."""

    def extract(self, soup: BeautifulSoup) -> SectionOutputT: ...


class RecordAssembler(Protocol[PayloadT]):
    """Contract for domain assemblers that compose final export records."""

    def assemble(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


class RecordFactory(Protocol[RecordT]):
    """Contract for model factories building typed record instances."""

    record_type: str

    def build(self, record: Mapping[str, Any]) -> RecordT: ...
