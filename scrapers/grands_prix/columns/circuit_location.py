from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.helpers.constructor_parsing import (
    ConstructorParsingHelpers,
)
from scrapers.base.table.columns.types import FuncColumn

if TYPE_CHECKING:
    from models.records.link import LinkRecord


class LocationColumn(FuncColumn):
    def __init__(self) -> None:
        super().__init__(self._parse_location)

    def _parse_location(self, ctx) -> dict[str, Any] | None:
        links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
        clean_text = clean_wiki_text(ctx.clean_text or "")

        if not links and not clean_text:
            return None

        circuit: LinkRecord
        layout: str | None = None

        if links:
            circuit = links[0]
            layout = ConstructorParsingHelpers.extract_layout_text(
                clean_text,
                circuit.get("text") or "",
            )
        else:
            circuit = {"text": clean_text, "url": None}

        if layout:
            return {"circuit": circuit, "layout": layout}
        return {"circuit": circuit}
