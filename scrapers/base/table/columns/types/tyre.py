from __future__ import annotations

from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn

_TYRE_NAME_BY_CODE = {
    "A": "Avon",
    "B": "Bridgestone",
    "C": "Continental",
    "D": "Dunlop",
    "E": "Englebert",
    "F": "Firestone",
    "G": "Goodyear",
    "M": "Michelin",
    "P": "Pirelli",
}


class TyreColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return None
        code = text[0].upper()
        full_name = _TYRE_NAME_BY_CODE.get(code)
        if not full_name:
            return code

        links = normalize_links(ctx.links or [], strip_marks=True, drop_empty=True)
        if links:
            link = links[0]
            return {**link, "text": full_name}

        return {"text": full_name, "url": None}
