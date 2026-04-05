from __future__ import annotations

import re
from typing import Any

from models.services import parse_seasons
from models.value_objects.season_ref import SeasonRef
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn

_YEAR_PATTERN = re.compile(r"^\d{4}$")
_YEAR_IN_URL_PATTERN = re.compile(r"(?<!\d)\d{4}(?!\d)")


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        season_refs = parse_seasons(ctx.clean_text)
        if not season_refs or not ctx.links:
            return [season.to_dict() for season in season_refs]

        url_by_year: dict[str, str] = {}
        for link in ctx.links:
            text = (link.get("text") or "").strip()
            url = link.get("url") or ""
            if _YEAR_PATTERN.match(text) and url:
                url_by_year[text] = url

        if not url_by_year:
            return [season.to_dict() for season in season_refs]

        result = []
        for season in season_refs:
            year_str = str(season.year)
            url = url_by_year.get(year_str) or self._derive_url(year_str, url_by_year)
            if url is None:
                url = season.url
            result.append(SeasonRef(year=season.year, url=url).to_dict())
        return result

    @staticmethod
    def _derive_url(year: str, url_by_year: dict[str, str]) -> str | None:
        for linked_year, linked_url in url_by_year.items():
            match = _YEAR_IN_URL_PATTERN.search(linked_url)
            if match and match.group() == linked_year:
                return (
                    linked_url[: match.start()]
                    + year
                    + linked_url[match.end() :]
                )
        return None
