from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar

if TYPE_CHECKING:
    from collections.abc import Mapping

    from bs4 import BeautifulSoup

PayloadT_contra = TypeVar("PayloadT_contra", contravariant=True)
SectionOutputT_co = TypeVar("SectionOutputT_co", covariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)


class SectionService(Protocol[SectionOutputT_co]):
    """Contract for domain section extraction services."""

    def extract(self, soup: BeautifulSoup) -> SectionOutputT_co: ...


class RecordAssembler(Protocol[PayloadT_contra]):
    """Contract for domain assemblers that compose final export records."""

    def assemble(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


class RecordFactory(Protocol[RecordT_co]):
    """Contract for model factories building typed record instances."""

    record_type: str

    def build(self, record: Mapping[str, Any]) -> RecordT_co: ...
