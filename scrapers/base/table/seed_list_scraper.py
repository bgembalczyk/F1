from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar
from warnings import warn

from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.schema import TableSchema
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.base.table.scraper import F1TableScraper
from scrapers.wiki.component_metadata import LIST_SCRAPER_KIND
from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.component_metadata import build_component_metadata


class SeedListTableScraper(F1TableScraper):
    """Wspólna baza dla scraperów seed/list opartych o tabelę."""

    options_profile: ClassVar[str | None] = "seed_soft"
    options_domain: ClassVar[str | None] = None

    domain: ClassVar[str | None] = None
    default_output_path: ClassVar[str | None] = None
    legacy_output_path: ClassVar[str | None] = None
    output_basename: ClassVar[str | None] = None

    COMPONENT_METADATA: ClassVar[ComponentMetadata | None] = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.options_domain is None:
            cls.options_domain = cls.domain

        if cls.COMPONENT_METADATA is not None or not cls.domain:
            return

        if cls.default_output_path is None or cls.legacy_output_path is None:
            basename = cls.output_basename or f"complete_{cls.domain}"
            cls.default_output_path = cls.default_output_path or (
                f"raw/{cls.domain}/seeds/{basename}"
            )
            cls.legacy_output_path = (
                cls.legacy_output_path or f"{cls.domain}/{basename}"
            )

        cls.COMPONENT_METADATA = build_component_metadata(
            domain=cls.domain,
            kind=LIST_SCRAPER_KIND,
            default_output_path=cls.default_output_path,
            legacy_output_path=cls.legacy_output_path,
        )

    @classmethod
    def build_config(
        cls,
        *,
        url: str,
        section_id: str | None = None,
        expected_headers: Sequence[str] | None = None,
        columns=None,
        schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None,
        table_css_class: str = "wikitable",
        record_factory=None,
        model_class: type | None = None,
    ) -> ScraperConfig:
        warn(
            "SeedListTableScraper.build_config is deprecated; "
            "use scrapers.base.table.config.build_scraper_config.",
            DeprecationWarning,
            stacklevel=2,
        )
        return build_scraper_config(
            url=url,
            section_id=section_id,
            expected_headers=expected_headers,
            columns=columns,
            schema=schema,
            table_css_class=table_css_class,
            record_factory=record_factory,
            model_class=model_class,
        )
