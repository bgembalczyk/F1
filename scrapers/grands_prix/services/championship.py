from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.adapters import HtmlRowBackgroundColorAdapter
from scrapers.grands_prix.helpers.constants import BACKGROUND_MAP
from scrapers.grands_prix.helpers.constants import DEFAULT_CHAMPIONSHIP
from scrapers.grands_prix.helpers.constants import UNKNOWN_CHAMPIONSHIP

if TYPE_CHECKING:
    from bs4 import Tag


class GrandPrixChampionshipResolver:
    """Domain service mapping normalized row color to championship domain value."""

    def __init__(
        self,
        *,
        row_background_adapter: HtmlRowBackgroundColorAdapter | None = None,
    ) -> None:
        self._row_background_adapter = row_background_adapter or HtmlRowBackgroundColorAdapter()

    def resolve(self, row: Tag) -> str:
        color = self._row_background_adapter.extract(row)
        if color is None:
            return DEFAULT_CHAMPIONSHIP
        return BACKGROUND_MAP.get(color, UNKNOWN_CHAMPIONSHIP)
