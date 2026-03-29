from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

PayloadT_contra = TypeVar("PayloadT_contra", contravariant=True)
SectionOutputT_co = TypeVar("SectionOutputT_co", covariant=True)
class RecordAssemblerProtocol(Protocol[PayloadT_contra]):
    """Contract for domain assemblers that compose final export records."""

    def assemble(self, payload: PayloadT_contra) -> dict[str, Any]: ...


class SectionExtractionServiceProtocol(Protocol[SectionOutputT_co]):
    """Contract for section extraction services in domain pipelines."""

    def extract(self, soup: BeautifulSoup) -> SectionOutputT_co: ...


RecordAssembler = RecordAssemblerProtocol
