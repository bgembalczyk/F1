from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.text import clean_wiki_text, extract_links_from_cell
from scrapers.base.helpers.wiki import build_full_url
from scrapers.base.errors import ScraperParseError
from scrapers.base.debug_dumps import (
    TablePipelineDebugContext,
    write_table_pipeline_dump,
)
from scrapers.base.logging import get_logger
from scrapers.base.null_policy import normalize_empty
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.parser import HtmlTableParser


class TablePipeline:
    """
    Pipeline parsowania tabel:
    - wybór tabeli na podstawie ScraperConfig,
    - parsowanie wierszy,
    - filtrowanie powtarzających się header-row,
    - mapowanie kolumn.
    """

    def __init__(
        self,
        *,
        config: ScraperConfig,
        include_urls: bool,
        skip_sentinel: object,
        model_fields: set[str] | None = None,
        run_id: str | None = None,
        debug_dir: str | Path | None = None,
    ) -> None:
        self.config = config
        self.include_urls = include_urls
        self.base_url = config.url
        self.skip_sentinel = skip_sentinel
        self.model_fields = model_fields
        self.run_id = run_id

        self.section_id = config.section_id
        self.expected_headers = config.expected_headers
        self.column_map = config.column_map
        self.columns = config.columns
        self.table_css_class = config.table_css_class
        self.default_column: BaseColumn = config.default_column or AutoColumn()
        self.record_factory = config.record_factory
        self.fragment: str | None = None
        self.logger = get_logger(self.__class__.__name__)
        self._normalized_empty_cells = 0
        self.debug_dir = Path(debug_dir) if debug_dir else None
        if not self.section_id:
            fragment = urlsplit(config.url).fragment
            if fragment:
                self.fragment = fragment

    def set_run_id(self, run_id: str | None) -> None:
        self.run_id = run_id

    def parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        self._normalized_empty_cells = 0
        section_hint = self.section_id or self.fragment
        candidate_tables = find_section_elements(
            soup,
            section_hint,
            ["table"],
            class_=self.table_css_class,
        )
        self.logger.debug(
            "TablePipeline detected %d tables (section_id=%s fragment=%s run_id=%s)",
            len(candidate_tables),
            self.section_id,
            self.fragment,
            self.run_id,
        )
        parser = HtmlTableParser(
            section_id=self.section_id,
            fragment=self.fragment,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(soup)):
            record = self.parse_cells(row.headers, row.cells, row_index=row_index)
            if record:
                records.append(record)

        self.logger.debug(
            "TablePipeline parsed %d row(s) from %d table(s) (section_id=%s run_id=%s)",
            len(records),
            len(candidate_tables),
            section_hint,
            self.run_id,
        )

        if self._normalized_empty_cells:
            self.logger.debug(
                "TablePipeline normalized %d empty cell(s) (run_id=%s)",
                self._normalized_empty_cells,
                self.run_id,
            )

        return records

    def parse_row(
        self,
        row: Mapping[str, Tag],
        *,
        row_index: int | None = None,
    ) -> Any:
        record: dict[str, Any] = {}

        for header, cell in row.items():
            if not isinstance(header, str):
                continue
            if header in {"__row__", "_row", "__tr__"}:
                continue
            self._apply_cell(record, header, cell, row_index=row_index)

        return self._finalize_record(record)

    def parse_cells(
        self,
        headers: Sequence[str],
        cells: Sequence[Tag],
        *,
        row_index: int | None = None,
    ) -> Any:
        record: dict[str, Any] = {}
        for header, cell in zip(headers, cells):
            self._apply_cell(record, header, cell, row_index=row_index)
        return self._finalize_record(record)

    def _finalize_record(self, record: dict[str, Any]) -> Any:
        if not record or self.record_factory is None:
            return record
        if isinstance(self.record_factory, type):
            payload = record
            if self.model_fields:
                payload = {
                    key: value
                    for key, value in record.items()
                    if key in self.model_fields
                }
            instance = self.record_factory(**payload)
            return instance
        return self.record_factory(record)

    @staticmethod
    def _cell_html(cell: Tag | None) -> str | None:
        if cell is None:
            return None
        return cell.decode_contents()

    def _dump_parse_context(
        self,
        *,
        header: str,
        row_index: int | None,
        cell_html: str | None,
        error: Exception,
    ) -> None:
        if self.debug_dir is None:
            return
        context = TablePipelineDebugContext(
            url=self.base_url,
            section_id=self.section_id,
            header=header,
            row_index=row_index,
            run_id=self.run_id,
        )
        dump_path = write_table_pipeline_dump(
            self.debug_dir,
            context=context,
            cell_html=cell_html,
            error=error,
        )
        self.logger.warning("Saved table pipeline debug dump: %s", dump_path)

    def _normalize_cell(self, header: str, cell: Tag) -> tuple[str, str, str | None]:
        key = self.column_map.get(header, normalize_header(header))
        raw_text = cell.get_text(" ", strip=True)
        clean_text = clean_wiki_text(raw_text)
        normalized = normalize_empty(clean_text)
        if normalized is None and clean_text == "":
            self._normalized_empty_cells += 1
        return key, raw_text, normalized

    def _extract_links(self, cell: Tag) -> list[LinkRecord]:
        if not self.include_urls:
            return []
        return extract_links_from_cell(
            cell,
            full_url=lambda href: build_full_url(self.base_url, href),
        )

    def _select_column(self, key: str, header: str) -> BaseColumn:
        return self.columns.get(key) or self.columns.get(header) or self.default_column

    def _apply_cell(
        self,
        record: dict[str, Any],
        header: str,
        cell: Tag,
        *,
        row_index: int | None = None,
    ) -> None:
        cell_html = self._cell_html(cell)
        key, raw_text, clean_text = self._normalize_cell(header, cell)
        links = self._extract_links(cell)

        ctx = ColumnContext(
            header=header,
            key=key,
            raw_text=raw_text,
            clean_text=clean_text,
            links=links,
            cell=cell,
            skip_sentinel=self.skip_sentinel,
            model_fields=self.model_fields,
        )

        col = self._select_column(key, header)
        try:
            col.apply(ctx, record)
        except Exception as exc:
            self._dump_parse_context(
                header=header,
                row_index=row_index,
                cell_html=cell_html,
                error=exc,
            )
            self.logger.exception(
                "Failed parsing column (header=%s key=%s row_index=%s base_url=%s raw_text=%s)",
                header,
                key,
                row_index,
                self.base_url,
                raw_text,
            )
            row_label = row_index if row_index is not None else "unknown"
            raise ScraperParseError(
                f"Failed parsing column {header} in row {row_label}",
                url=self.base_url,
                cause=exc,
            ) from exc
