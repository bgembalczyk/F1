from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.helpers.links import normalize_links


class CalendarCircuitColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        links = normalize_links(ctx.links or [], strip_marks=True, drop_empty=True)
        if not links:
            text = (ctx.clean_text or "").strip()
            return {"circuit": {"text": text, "url": None}} if text else None

        circuit = links[0]
        location = links[1] if len(links) > 1 else None
        data = {"circuit": circuit}
        if location:
            data["location"] = location
        return data
