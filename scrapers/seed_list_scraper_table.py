from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from warnings import warn

from bs4 import BeautifulSoup

from scrapers.component_metadata_wiki import LIST_SCRAPER_KIND
from scrapers.component_metadata_wiki import ComponentMetadata
from scrapers.component_metadata_wiki import build_component_metadata
from scrapers.config_table import TableConfig
from scrapers.config_table import build_scraper_config
from scrapers.schema_table import TableSchema
from scrapers.schema_table import TableSchemaBuilder
from scrapers.scraper_table import F1TableScraper
from scrapers.section.selection_strategy import WikipediaSectionByIdSelectionStrategy
from scrapers.table_schema_dsl import TableSchemaDSL

if TYPE_CHECKING:
    from collections.abc import Sequence


class SeedListTableScraper(F1TableScraper):
    """Wspólna baza dla scraperów seed/list opartych o tabelę.

    Includes section-based table parsing functionality (formerly
    ``DeclarativeSectionTableParseMixin``).
    """

    options_profile: ClassVar[str | None] = "seed_soft"
    options_domain: ClassVar[str | None] = None

    domain: ClassVar[str | None] = None
    default_output_path: ClassVar[str | None] = None
    legacy_output_path: ClassVar[str | None] = None
    output_basename: ClassVar[str | None] = None

    COMPONENT_METADATA: ClassVar[ComponentMetadata | None] = None

    # Class attributes used by the declarative section parsing
    section_label: ClassVar[str | None] = None
    section_parser_class: ClassVar[type[Any] | None] = None

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

    # ------------------------------------------------------------------
    # Section-table parsing (formerly DeclarativeSectionTableParseMixin)
    # ------------------------------------------------------------------

    def _diagnostic_context(
        self,
        *,
        domain: str,
        section_label: str | None,
    ) -> str:
        details = [f"domain={domain!r}"]
        if section_label is not None:
            details.append(f"section_label={section_label!r}")
        return ", ".join(details)

    def parse_section_or_fallback(
        self,
        soup: BeautifulSoup,
        *,
        domain: str,
        parser_factory: Callable[[], Any],
        section_label: str | None = None,
    ) -> list[Any]:
        """Parse records from configured section, then fallback to full soup."""
        section_id = self.config.section_id
        if not section_id:
            return super()._parse_soup(soup)

        section_fragment = (
            WikipediaSectionByIdSelectionStrategy().extract_section_by_id(
                soup,
                section_id,
                domain=domain,
            )
        )
        if section_fragment is None:
            context = self._diagnostic_context(
                domain=domain,
                section_label=section_label,
            )
            msg = f"Nie znaleziono sekcji o id={section_id!r} ({context})"
            raise RuntimeError(msg)

        parser = parser_factory()
        try:
            return parser.parse(section_fragment).records
        except RuntimeError:
            return super()._parse_soup(soup)

    def _build_section_parser(self) -> Any:
        if self.section_parser_class is None:
            msg = f"{self.__class__.__name__} must define section_parser_class"
            raise RuntimeError(msg)

        return self.section_parser_class(
            config=self.config,
            section_label=self.section_label,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        if self.domain is None:
            return super()._parse_soup(soup)

        return self.parse_section_or_fallback(
            soup,
            domain=self.domain,
            section_label=self.section_label,
            parser_factory=self._build_section_parser,
        )

    # ------------------------------------------------------------------

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
