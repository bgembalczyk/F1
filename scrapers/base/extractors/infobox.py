from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.debug_dumps import write_infobox_dump
from scrapers.base.infobox.field_mapper import InfoboxFieldMapper
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.logging import get_logger


class InfoboxExtractor:
    def __init__(
        self,
        *,
        parser: InfoboxHtmlParser | None = None,
        mapper: InfoboxFieldMapper | None = None,
        logger=None,
        debug_dir: str | Path | None = None,
        run_id: str | None = None,
        url: str | None = None,
    ) -> None:
        self.logger = logger or get_logger(self.__class__.__name__)
        self.parser = parser or InfoboxHtmlParser()
        self.mapper = mapper or InfoboxFieldMapper(logger=self.logger)
        self.debug_dir = Path(debug_dir) if debug_dir else None
        self.run_id = run_id
        self.url = url

    def extract(self, soup: BeautifulSoup) -> dict[str, Any]:
        self.logger.debug("InfoboxExtractor start (run_id=%s)", self.run_id)
        try:
            raw = self.parser.parse(soup)
            mapped = self.mapper.map(raw)
        except Exception:
            if self.debug_dir is not None:
                table = self.parser.find_infobox(soup)
                if table is not None:
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
        rows = mapped.get("rows", {}) if isinstance(mapped, dict) else {}
        self.logger.debug(
            "InfoboxExtractor extracted %d row(s) (run_id=%s)",
            len(rows),
            self.run_id,
        )
        return mapped
