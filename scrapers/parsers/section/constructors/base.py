import logging

from bs4 import BeautifulSoup

from scrapers.config import ScraperConfig
from scrapers.parser_table import HtmlTableParser
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result
from scrapers.wiki.parsers.elements.wiki_table import WikiTableBaseParser

logger = logging.getLogger(__name__)


class ConstructorsSectionParser(WikiSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None,
        include_urls: bool,
        normalize_empty_values: bool,
        table_parser: WikiTableBaseParser,
    ) -> None:
        super().__init__()
        self._include_urls = include_urls
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "constructors",
            section_label=section_label or "Constructors",
            domain="constructors",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )
        self._table_parser = table_parser
        self._html_table_parser = HtmlTableParser()

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
                rows = self._html_table_parser.parse_table(table)
                headers = rows[0].headers if rows else []
                logger.warning(
                    "Constructors section parser '%s': first table headers=%s.",
                    self._parser.section_label,
                    headers,
                )
                row_maps = [
                    {
                        header: cell.get_text(" ", strip=True)
                        for header, cell in zip(row.headers, row.cells, strict=False)
                    }
                    for row in rows
                ]
                self._table_parser.parse({"headers": headers, "rows": row_maps})
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
