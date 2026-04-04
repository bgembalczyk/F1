from dataclasses import replace
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.logging import get_logger
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline


class TableExtractor:
    def __init__(
        self,
        *,
        config: ScraperConfig,
        include_urls: bool,
        normalize_empty_values: bool = True,
        model_fields: set[str] | None = None,
        debug_dir: str | Path | None = None,
    ) -> None:
        raw_config = replace(config, record_factory=None)
        self.pipeline = TablePipeline(
            config=raw_config,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            model_fields=model_fields,
            debug_dir=debug_dir,
        )
        self.logger = get_logger(self.__class__.__name__)

    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        self.logger.debug(
            "TableExtractor start (run_id=%s)",
            self.pipeline.run_id,
        )
        records = self.pipeline.parse_soup(soup)
        self.logger.debug(
            "TableExtractor extracted %d record(s) (run_id=%s)",
            len(records),
            self.pipeline.run_id,
        )
        return records
