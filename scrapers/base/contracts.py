from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import TypeVar

PayloadT_contra = TypeVar("PayloadT_contra", contravariant=True)
SectionOutputT_co = TypeVar("SectionOutputT_co", covariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)


class RecordAssembler(Protocol[PayloadT_contra]):
    """Contract for domain assemblers that compose final export records."""

    def assemble(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...
