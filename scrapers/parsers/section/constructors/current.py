from scrapers.config_table import TableScraperConfig
from typing import Any

from bs4 import BeautifulSoup

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.configs.public import TableConfig
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.table.constructor.current import CurrentConstructorsTableParser


class CurrentConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: TableConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_mapping_parser=CurrentConstructorsTableParser(),
        )
