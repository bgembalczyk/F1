from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from warnings import warn

from scrapers.component_metadata_wiki import LIST_SCRAPER_KIND
from scrapers.component_metadata_wiki import ComponentMetadata
from scrapers.component_metadata_wiki import build_component_metadata
from scrapers.config_table import TableConfig
from scrapers.config_table import build_scraper_config
from scrapers.family_contracts import ListScraperContract
from scrapers.schema_table import TableSchema
from scrapers.schema_table import TableSchemaBuilder
from scrapers.scraper_table import F1TableScraper
from scrapers.table_schema_dsl import TableSchemaDSL

if TYPE_CHECKING:
    from collections.abc import Sequence


class SeedListTableScraper(F1TableScraper, ListScraperContract):
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
    ) -> TableConfig:
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
