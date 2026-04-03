from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.source_catalog import CONSTRUCTORS_LIST
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config

if TYPE_CHECKING:
    from collections.abc import Sequence
    from scrapers.base.table.dsl.column import ColumnSpec


def build_constructor_list_config(
    *,
    section_id: str,
    expected_headers: Sequence[str],
    columns: Sequence[ColumnSpec],
) -> ScraperConfig:
    return build_scraper_config(
        url=CONSTRUCTORS_LIST.base_url,
        section_id=section_id,
        expected_headers=expected_headers,
        columns=columns,
        record_factory=RECORD_FACTORIES.builders("constructor"),
    )
