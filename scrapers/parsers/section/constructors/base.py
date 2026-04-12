import logging

from bs4 import BeautifulSoup

from scrapers.configs.public import TableConfig
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.base_section_parser import BaseSectionParser
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

logger = logging.getLogger(__name__)


class ConstructorsSectionParser(BaseSectionParser):
    def __init__(
        self,
        *,
        config: TableConfig,
        section_label: str | None,
        include_urls: bool,
        normalize_empty_values: bool,
        table_html_parser: WikiTableHtmlParser | None = None,
        table_domain_mapper: WikiTableBaseMapper | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self._toolbox = toolbox or build_default_section_toolbox()
        self._include_urls = include_urls
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "constructors",
            section_label=section_label or "Constructors",
            domain="constructors",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )
        self._table_html_parser = (
            table_html_parser or self._toolbox.element_parsers.table_parser
        )
        if table_domain_mapper is None:
            msg = "table_domain_mapper must be provided"
            raise ValueError(msg)
        self._table_domain_mapper = table_domain_mapper

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        logger.warning(
            "Constructors section parser '%s': start parse.",
            self._parser.section_label,
        )
        table = section_fragment.find("table", class_="wikitable")
        logger.warning(
            "Constructors section parser '%s': first wikitable found=%s.",
            self._parser.section_label,
            table is not None,
        )
        if table is not None:
            try:
                parsed_table = self._table_html_parser.parse(table)
                headers = parsed_table.get("headers", [])
                logger.warning(
                    "Constructors section parser '%s': first table headers=%s.",
                    self._parser.section_label,
                    headers,
                )
                self._table_domain_mapper.map(parsed_table)
            except RuntimeError:
                logger.warning(
                    "Constructors section parser '%s': "
                    "lightweight table pre-parse failed.",
                    self._parser.section_label,
                )
        try:
            return self._parser.parse(section_fragment)
        except RuntimeError:
            logger.warning(
                "Constructors section parser '%s': full section parse failed, "
                "trying table-only fallback.",
                self._parser.section_label,
            )
            if table is not None:
                table_only_fragment = BeautifulSoup(str(table), "html.parser")
                try:
                    return self._parser.parse(table_only_fragment)
                except RuntimeError:
                    logger.warning(
                        "Constructors section parser '%s': table-only fallback failed.",
                        self._parser.section_label,
                    )
            logger.warning(
                "Skipping constructors section '%s': matching table not found.",
                self._parser.section_label,
            )
            return build_section_parse_result(
                section_id=self._parser.section_id,
                section_label=self._parser.section_label,
                records=[],
                parser=self.__class__.__name__,
                source="wikipedia",
                extras={"domain": "constructors", "skipped": True},
            )
