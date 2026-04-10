from abc import ABC
from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.configs.table_scraper_config_resolver import resolve_table_scraper_config
from scrapers.base.helpers.config_factory import build_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.services.table_scraper_runtime import build_table_extractor
from scrapers.base.services.table_scraper_runtime import ensure_record_factory_validator
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig as TableScraperConfig
from scrapers.base.table.row import TableRow
from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.transformers.record_factory import RecordFactoryTransformer
from scrapers.wiki.scraper_wiki import AbstractWikiScraper


class AbstractTableScraper(AbstractWikiScraper, ABC):
    """Template base class for wiki table scrapers."""

    CONFIG: TableScraperConfig | None = None
    options_domain: str | None = None
    options_profile: str | None = None
    default_column: BaseColumn = AutoColumn()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
    ) -> None:
        resolved_options = self._resolve_options(options)
        super().__init__(options=resolved_options)

        resolved_config = resolve_table_scraper_config(self, config)
        self._apply_config(resolved_config)
        self.extractor = self.build_parser()
        ensure_record_factory_validator(
            validator=self.validator,
            record_factory=self.record_factory,
        )

    def _resolve_options(self, options: ScraperOptions | None) -> ScraperOptions:
        if options is None:
            if self.options_profile is None:
                options = ScraperOptions()
            else:
                options = build_scraper_options(
                    domain=self.options_domain,
                    profile=self.options_profile,
                    scraper_cls=type(self),
                )
        elif self.options_profile is not None:
            options = build_scraper_options(
                domain=self.options_domain,
                profile=self.options_profile,
                options=options,
                scraper_cls=type(self),
            )
        return self.extend_options(options)

    def _apply_config(self, config: TableScraperConfig) -> None:
        self.config = config
        self.url = config.url
        self.section_id = config.section_id
        self.expected_headers = config.expected_headers
        self.column_map = config.column_map
        self.columns = config.columns
        self.table_css_class = config.table_css_class
        self.record_factory = config.record_factory
        self.model_class = config.model_class
        self.default_column = config.default_column or AutoColumn()

    def extend_options(self, options: ScraperOptions) -> ScraperOptions:
        return options

    def build_parser(self):
        return build_table_extractor(
            config=self.config,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
            model_fields=self._model_fields(),
            debug_dir=self.debug_dir,
        )

    def parse_records(self, soup: BeautifulSoup) -> list[Any]:
        self.extractor.pipeline.set_run_id(getattr(self, "_run_id", None))
        return self.extractor.extract(soup)

    def build_record(self, row: TableRow | dict[str, Any]) -> Any | None:
        if isinstance(row, dict):
            headers = list(row.keys())
            cells = list(row.values())
            return self.extractor.pipeline.parse_cells(headers, cells)
        return self.extractor.pipeline.parse_cells(
            row.headers,
            row.cells,
            header_cells=row.header_cells,
        )

    def parse_row(self, row: TableRow | dict[str, Any]) -> Any | None:
        return self.build_record(row)

    def _model_fields(self) -> set[str] | None:
        model_class = getattr(self, "model_class", None)
        record_factory = getattr(self, "record_factory", None)
        if model_class is None and isinstance(record_factory, type):
            model_class = record_factory
        if not model_class:
            return None

        if isinstance(model_class, type) and is_dataclass(model_class):
            return {f.name for f in fields(model_class)}

        model_fields = getattr(model_class, "model_fields", None)
        if model_fields:
            return set(model_fields)

        pydantic_fields = getattr(model_class, "__fields__", None)
        if pydantic_fields:
            return set(pydantic_fields)

        return None

    def _apply_transformers(self, records: list[Any]) -> list[Any]:
        transformers = list(self.transformers)
        if self.record_factory is not None:
            transformers.append(RecordFactoryTransformer(self.record_factory))
        return apply_transformers(transformers, records, logger=self.logger)


class F1TableScraper(AbstractTableScraper):
    """Backward-compatible concrete table scraper."""


__all__ = ["AbstractTableScraper", "F1TableScraper"]
