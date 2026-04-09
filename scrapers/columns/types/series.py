from typing import Any

from scrapers.columns.helpers.split_series import split_series
from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.links import normalize_links


class SeriesColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        series_text, class_text = split_series(text)
        links = normalize_links(ctx.links or [])
        series_link = links[0] if links else None

        series_value: dict[str, str | None] | str | None
        if series_link:
            series_value = {"text": series_link["text"], "url": series_link["url"]}
        else:
            series_value = series_text

        if class_text:
            return {"series": series_value, "class": class_text}
        return {"series": series_value}
