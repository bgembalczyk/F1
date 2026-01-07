import logging
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.options import ScraperOptions
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)

logger = logging.getLogger(__name__)


class RedFlaggedRacesBaseScraper(F1TableScraper):
    # Subclasses can override to provide fallback section IDs
    alternative_section_ids: List[str] = []
    
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config=None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = list(options.transformers or []) + [
            FailedToMakeRestartTransformer(),
        ]
        super().__init__(options=options, config=config)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        # Try the primary section_id first, then alternatives, then None (whole document)
        # Filter out None from the primary section_id to avoid duplication
        section_ids_to_try = (
            [self.section_id] if self.section_id is not None else []
        ) + self.alternative_section_ids + [None]
        
        table = None
        parser = None
        
        for section_id in section_ids_to_try:
            logger.debug(f"Trying to find table with section_id={section_id!r}")
            current_parser = HtmlTableParser(
                section_id=section_id,
                expected_headers=self.expected_headers,
                table_css_class=self.table_css_class,
            )
            try:
                table = current_parser._find_table(soup)
                parser = current_parser
                logger.info(f"Successfully found table with section_id={section_id!r}")
                break
            except RuntimeError as e:
                logger.debug(f"Failed to find table with section_id={section_id!r}: {e}")
                continue
        
        if table is None:
            # Extract available section IDs from MediaWiki headlines
            # This assumes Wikipedia's standard MediaWiki structure
            available_sections = [
                span.get('id', 'no-id') 
                for span in soup.select('.mw-headline')
            ]
            # Show first 10 sections for readability
            sections_preview = available_sections[:10]
            if len(available_sections) > 10:
                sections_preview.append(f"... and {len(available_sections) - 10} more")
            
            error_msg = (
                f"Nie znaleziono pasującej tabeli. "
                f"Próbowano sekcji: {section_ids_to_try}. "
                f"Dostępne sekcje na stronie: {sections_preview}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)

        records: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        rows = table.find_all("tr")[header_rows:]
        for row_index, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            if not cells or all(not cell.get_text(strip=True) for cell in cells):
                continue

            cleaned_cells = [
                clean_wiki_text(cell.get_text(" ", strip=True)) for cell in cells
            ]
            if parser._is_footer_row(cells, cleaned_cells, headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            expanded_cells = parser._expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )
            record = self.extractor.pipeline.parse_cells(
                headers, expanded_cells, row_index=row_index
            )
            if record:
                records.append(record)

        return records
