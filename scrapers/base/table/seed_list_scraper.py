from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.scraper import F1TableScraper
from scrapers.wiki.component_metadata import ComponentMetadata

if TYPE_CHECKING:
    from collections.abc import Sequence

    from scrapers.base.options import ScraperOptions
    from scrapers.base.post_processors import RecordPostProcessor
    from scrapers.base.table.config import ScraperConfig
    from scrapers.base.table.dsl.table_schema import TableSchemaDSL
    from scrapers.base.table.schema import TableSchema
    from scrapers.base.table.schema import TableSchemaBuilder
    from scrapers.base.transformers.record_transformer import RecordTransformer


class BaseSeedListScraper(F1TableScraper):
    """Wspólna baza dla scraperów seed/list opartych o tabelę."""

    options_profile: ClassVar[str | None] = "soft_seed"
    options_domain: ClassVar[str | None] = None

    domain: ClassVar[str | None] = None
    default_output_path: ClassVar[str | None] = None
    legacy_output_path: ClassVar[str | None] = None

    normalize_empty_values: ClassVar[bool | None] = None
    default_transformers: ClassVar[Sequence[RecordTransformer]] = ()
    default_post_processors: ClassVar[Sequence[RecordPostProcessor]] = ()

    COMPONENT_METADATA: ClassVar[ComponentMetadata | None] = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.options_domain is None:
            cls.options_domain = cls.domain

        if (
            cls.COMPONENT_METADATA is None
            and cls.domain
            and cls.default_output_path
            and cls.legacy_output_path
        ):
            cls.COMPONENT_METADATA = ComponentMetadata.build_layer_one_list_scraper(
                domain=cls.domain,
                default_output_path=cls.default_output_path,
                legacy_output_path=cls.legacy_output_path,
            )

    def extend_options(self, options: ScraperOptions) -> ScraperOptions:
        options = super().extend_options(options)

        if self.normalize_empty_values is not None:
            options.normalize_empty_values = self.normalize_empty_values

        options.transformers = [
            *list(options.transformers or []),
            *self.default_transformers,
        ]
        options.post_processors = [
            *list(options.post_processors or []),
            *self.default_post_processors,
        ]
        return options

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


# Backward compatibility alias
SeedListTableScraper = BaseSeedListScraper
