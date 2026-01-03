from typing import Any
from typing import Dict
from typing import Optional

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.helpers import extract_layout_text
from scrapers.base.table.columns.types.func import FuncColumn


class LocationColumn(FuncColumn):
    def __init__(self) -> None:
        super().__init__(self._parse_location)

    def _parse_location(self, ctx) -> Dict[str, Any] | None:
        links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
        clean_text = clean_wiki_text(ctx.clean_text or "")

        if not links and not clean_text:
            return None

        circuit: LinkRecord
        layout: Optional[str] = None

        if links:
            circuit = links[0]
            layout = extract_layout_text(clean_text, circuit.get("text") or "")
        else:
            circuit = {"text": clean_text, "url": None}

        if layout:
            return {"circuit": circuit, "layout": layout}
        return {"circuit": circuit}
