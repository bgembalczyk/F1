from scrapers.config_table import TableScraperConfig
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.table.constructor.current import CurrentConstructorsTableParser


class CurrentConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: TableScraperConfig,
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
