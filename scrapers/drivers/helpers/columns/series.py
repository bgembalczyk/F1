from __future__ import annotations

import re
from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SeriesColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        series_text, class_text = _split_series(text)
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


def _split_series(text: str) -> tuple[str, str | None]:
    parts = [p.strip() for p in re.split(r"\s*-\s*", text, maxsplit=1)]
    if len(parts) == 1:
        return text, None
    return parts[0], parts[1] or None
