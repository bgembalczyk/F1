from bs4 import BeautifulSoup

from scrapers.configs.public import TableConfig
from scrapers.parsers.current_constructors_table_mapper import (
    CurrentConstructorsTableMapper,
)
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.section.parse_results import SectionParseResult


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
            table_html_parser=WikiTableHtmlParser(),
            table_domain_mapper=CurrentConstructorsTableMapper(),
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return super().parse(section_fragment)
