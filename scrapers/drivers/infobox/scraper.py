from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.debug_dumps import write_infobox_dump
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.drivers.infobox.parsers.career import InfoboxCareerParser
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.general import InfoboxGeneralParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.section_collector import InfoboxSectionCollector
from scrapers.drivers.infobox.parsers.title import InfoboxTitlesParser


class DriverInfoboxScraper:
    _IGNORED_SECTIONS = {"Awards", "Medal record", "Signature"}
    _GENERAL_KEYS = {
        "Born": "born",
        "Died": "died",
        "Parent": "parents",
        "Parents": "parents",
        "Parent(s)": "parents",
        "Relatives": "relatives",
        "Children": "children",
        "Cause of death": "cause_of_death",
    }

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        run_id: str | None = None,
        url: str | None = None,
    ) -> None:
        options = options or ScraperOptions()
        self.include_urls = options.include_urls
        self.record_factory = options.record_factory
        self.debug_dir = options.debug_dir
        self.wikipedia_base = InfoboxHtmlParser.WIKIPEDIA_BASE
        self.run_id = run_id
        self.url = url
        self.logger = get_logger(self.__class__.__name__)
        self._link_extractor = InfoboxLinkExtractor(
            include_urls=self.include_urls,
            wikipedia_base=self.wikipedia_base,
        )
        self._cell_parser = InfoboxCellParser(
            include_urls=self.include_urls,
            link_extractor=self._link_extractor,
        )
        self._general_parser = InfoboxGeneralParser(
            include_urls=self.include_urls,
            link_extractor=self._link_extractor,
            general_keys=self._GENERAL_KEYS,
        )
        self._titles_parser = InfoboxTitlesParser(self._link_extractor)
        self._career_parser = InfoboxCareerParser(self._cell_parser)
        self._section_collector = InfoboxSectionCollector()

    def parse(self, soup: BeautifulSoup) -> List[Any]:
        self.logger.debug("Infobox parse start (run_id=%s)", self.run_id)
        table = InfoboxHtmlParser.find_infobox(soup)
        if table is None:
            self.logger.debug("Infobox not found (run_id=%s)", self.run_id)
            return []
        rows_count = len(table.find_all("tr"))
        sections = self._section_collector.collect(table)
        total_rows = sum(len(section.get("rows", [])) for section in sections)
        self.logger.debug(
            "Infobox detected %d row(s) and %d section(s) (run_id=%s)",
            rows_count,
            len(sections),
            self.run_id,
        )
        try:
            parsed = self._parse_infobox_with_sections(table, sections)
        except Exception:
            if self.debug_dir is not None:
                dump_path = write_infobox_dump(
                    self.debug_dir,
                    html=str(table),
                    url=self.url,
                    run_id=self.run_id,
                )
                self.logger.warning(
                    "Saved infobox HTML dump: %s (url=%s)",
                    dump_path,
                    self.url,
                )
            raise
        self.logger.debug(
            "Infobox parsed %d row(s) across %d section(s) (run_id=%s)",
            total_rows,
            len(sections),
            self.run_id,
        )
        return [self._apply_record_factory(parsed)]

    def _apply_record_factory(self, record: Dict[str, Any]) -> Any:
        if self.record_factory is None:
            return record
        try:
            if isinstance(self.record_factory, type):
                return self.record_factory(**record)
            return self.record_factory(record)
        except Exception:
            self.logger.warning(
                "Infobox record_factory failed (run_id=%s). "
                "Falling back to raw record: %s",
                self.run_id,
                record,
                exc_info=True,
            )
            return record

    def _parse_infobox_with_sections(
        self, table: Tag, sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        general_section = sections[0] if sections else {"rows": []}

        parsed = {
            "title": self._infobox_title(table),
            "general": self._general_parser.parse(general_section.get("rows", [])),
            "championship_titles": [],
            "major_victories": [],
            "career": [],
            "previous_series": [],
        }

        for section in sections[1:]:
            title = section.get("title") or ""
            if title in self._IGNORED_SECTIONS:
                continue
            if title == "Championship titles":
                parsed["championship_titles"] = self._titles_parser.parse_titles(
                    section["rows"]
                )
                continue
            if title == "Major victories":
                parsed["major_victories"] = self._titles_parser.parse_titles(
                    section["rows"]
                )
                continue
            if title.endswith("career"):
                parsed["career"].append(
                    self._career_parser.parse_section(title, section)
                )
                continue
            if title == "Previous series":
                parsed["previous_series"] = self._titles_parser.parse_previous_series(
                    section["rows"]
                )
                continue

        return parsed

    def _infobox_title(self, table: Tag) -> str | None:
        caption = table.find("caption")
        if not caption:
            return None
        return clean_infobox_text(caption.get_text(" ", strip=True))
