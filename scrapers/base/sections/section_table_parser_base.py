from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_parse_result
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SectionTableParserBase(ABC):
    """Template-method base for section parsers built from one or many HTML tables."""

    def __init__(
        self,
        *,
        section_id: str,
        section_label: str,
        source: str = "wikipedia",
        metadata_extras: dict[str, Any] | None = None,
        include_heading_path: bool = False,
        include_source_table: bool = False,
    ) -> None:
        self._section_id = section_id
        self._section_label = section_label
        self._source = source
        self._metadata_extras = metadata_extras or {}
        self._table_parser = ArticleTablesParser(
            include_heading_path=include_heading_path,
            include_source_table=include_source_table,
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records: list[dict[str, Any]] = []
        for table_data in self.iter_table_data(section_fragment):
            table_classification = self.classify_table(table_data)
            if table_classification is None:
                continue
            table_pipeline = self.build_pipeline(
                table_data=table_data,
                table_classification=table_classification,
            )
            mapped = self.map_table_result(
                table_data=table_data,
                table_classification=table_classification,
                table_pipeline=table_pipeline,
            )
            if mapped is None:
                continue
            records.append(mapped)
        return self.build_result(records)

    def iter_table_data(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        return self._table_parser.parse(section_fragment)

    def classify_table(self, table_data: dict[str, Any]) -> Any | None:
        return table_data

    def build_pipeline(self, *, table_data: dict[str, Any], table_classification: Any) -> Any:
        return None

    @abstractmethod
    def map_table_result(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: Any,
        table_pipeline: Any,
    ) -> dict[str, Any] | None:
        """Transform a parsed table into a domain record (or skip with None)."""

    def build_result(self, records: list[dict[str, Any]]) -> SectionParseResult:
        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            parser=self.__class__.__name__,
            source=self._source,
            extras=self._metadata_extras,
        )
