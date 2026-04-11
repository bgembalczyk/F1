from typing import Any
from typing import Protocol

from scrapers.parsers.section.extraction_context import SectionExtractionContext


class NestedChildParser(Protocol):
    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]: ...
