from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

PayloadT_contra = TypeVar("PayloadT_contra", contravariant=True)
SectionOutputT_co = TypeVar("SectionOutputT_co", covariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)


class RecordAssembler(Protocol[PayloadT_contra]):
    """Contract for domain assemblers that compose final export records."""

    def assemble(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class ReportableScraper(Protocol):
    """Public contract for scrapers that can emit per-step quality reports."""

    def write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None: ...
