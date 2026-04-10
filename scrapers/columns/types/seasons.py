from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from models.services.season import parse_seasons
from models.value_objects.season_ref import SeasonRef
from scrapers.columns.helpers.constants import LAST_YEAR_FORMULA_ONE_SEASON
from scrapers.columns.helpers.constants import YEAR_IN_URL_PATTERN
from scrapers.columns.helpers.constants import YEAR_PATTERN
from scrapers.columns.types.base import BaseColumn
from scrapers.helpers.url import resolve_url
from scrapers.url_resolver import DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY

if TYPE_CHECKING:
    from scrapers.columns.types.context import ColumnContext


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        season_refs = parse_seasons(ctx.clean_text)
        if not season_refs:
            return [season.to_dict() for season in season_refs]

        url_by_year: dict[str, str] = {}
        for link in ctx.links:
            text = (link.get("text") or "").strip()
            url = link.get("url") or ""
            if YEAR_PATTERN.match(text) and url:
                url_by_year[text] = url

        result = []
        for season in season_refs:
            year_str = str(season.year)
            url = url_by_year.get(year_str) or self._derive_url(year_str, url_by_year)
            if url is None:
                url = self._build_season_url(year_str, url_by_year=url_by_year)
            result.append(SeasonRef(year=season.year, url=url).to_dict())
        return result

    @staticmethod
    def _derive_url(year: str, url_by_year: dict[str, str]) -> str | None:
        for linked_year, linked_url in url_by_year.items():
            match = YEAR_IN_URL_PATTERN.search(linked_url)
            if match and match.group() == linked_year:
                if "/wiki/" in linked_url:
                    base = linked_url.split("/wiki/", 1)[0]
                    return resolve_url(
                        base,
                        f"/wiki/{SeasonsColumn._season_page_title(year)}",
                        domain="seasons",
                    )
                return linked_url[: match.start()] + year + linked_url[match.end() :]
        return None

    @staticmethod
    def _build_season_url(year: str, *, url_by_year: dict[str, str]) -> str:
        base_url = next(iter(url_by_year.values()), "https://en.wikipedia.org/wiki")
        resolved = DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.fallback_canonical_url(
            domain="seasons",
            base_url=base_url,
            year=year,
            season_page_title=SeasonsColumn._season_page_title(year),
        )
        return (
            resolved
            or f"https://en.wikipedia.org/wiki/{SeasonsColumn._season_page_title(year)}"
        )

    @staticmethod
    def _season_page_title(year: str) -> str:
        season_type = (
            "Formula_One_season"
            if int(year) <= LAST_YEAR_FORMULA_ONE_SEASON
            else "Formula_One_World_Championship"
        )
        return f"{year}_{season_type}"


__all__ = ["SeasonsColumn"]
