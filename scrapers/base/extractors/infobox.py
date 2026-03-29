from pathlib import Path
from typing import Any
from typing import Literal

from bs4 import BeautifulSoup

from infrastructure.http_client.requests_shim.request_error import RequestError
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
        error_policy: Literal["retry", "skip", "fail-fast"] = "fail-fast",
        retry_attempts: int = 1,
    ) -> None:
        self.logger = logger or get_logger(self.__class__.__name__)
        self.parser = parser or InfoboxHtmlParser()
        self.mapper = mapper or InfoboxFieldMapper(logger=self.logger)
        self.debug_dir = Path(debug_dir) if debug_dir else None
        self.run_id = run_id
        self.url = url
        self.error_policy = error_policy
        self.retry_attempts = retry_attempts
        if self.error_policy not in {"retry", "skip", "fail-fast"}:
            msg = "error_policy must be one of: 'retry', 'skip', 'fail-fast'"
            raise ValueError(msg)
        if self.retry_attempts < 1:
            msg = "retry_attempts must be >= 1"
            raise ValueError(msg)

    def extract(self, soup: BeautifulSoup) -> dict[str, Any]:
        self.logger.debug("InfoboxExtractor start (run_id=%s)", self.run_id)
        mapped: dict[str, Any]
        attempts = self.retry_attempts if self.error_policy == "retry" else 1
        attempt = 0
        while True:
            try:
                raw = self.parser.parse(soup)
                mapped = self.mapper.map(raw)
                break
            except (
                KeyError,
                RequestError,
                ConnectionError,
                OSError,
                TimeoutError,
                ValueError,
            ):
                self._write_debug_dump_if_possible(soup)
                if self.error_policy == "skip":
                    return {}
                if self.error_policy == "retry" and attempt + 1 < attempts:
                    attempt += 1
                    continue
                raise
        rows = mapped.get("rows", {}) if isinstance(mapped, dict) else {}
        self.logger.debug(
            "InfoboxExtractor extracted %d row(s) (run_id=%s)",
            len(rows),
            self.run_id,
        )
        return mapped

    def _write_debug_dump_if_possible(self, soup: BeautifulSoup) -> None:
        if self.debug_dir is None:
            return
        table = self.parser.find_infobox(soup)
        if table is None:
            return
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
