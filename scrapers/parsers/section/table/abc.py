from __future__ import annotations

import inspect
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.table.wiki.article import ArticleTablesParser
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from scrapers.parsers.input_types import WikiParserInput
    from scrapers.section.parse_results import SectionParseResult


class SectionTableParserBase(BaseSectionParser, ABC):
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

    def parse(self, fragment: WikiParserInput) -> SectionParseResult:
        return self.parse_fragment(fragment)

    def parse_fragment(self, fragment: WikiParserInput) -> SectionParseResult:
        records: list[dict[str, Any]] = []
        for table_data in self._collect_tables(fragment):
            table_classification = self.classify_table(table_data)
            if table_classification is None:
                continue
            table_pipeline = self.build_pipeline(
                table_data=table_data,
                table_classification=table_classification,
            )
            mapped = self.parse_row(
                table_data=table_data,
                table_classification=table_classification,
                table_pipeline=table_pipeline,
            )
            if mapped is None:
                continue
            records.append(mapped)
        return self.build_result(records)

    def _collect_tables(
        self,
        fragment: WikiParserInput,
    ) -> list[dict[str, Any]]:
        """Collect table payloads used by the section table template pipeline."""

        return self.parse_group(fragment)

    def parse_group(
        self,
        fragment: WikiParserInput,
    ) -> list[dict[str, Any]]:
        return self._table_parser.parse(fragment)

    def classify_table(self, table_data: dict[str, Any]) -> Any | None:
        return table_data

    def build_pipeline(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: Any,
    ) -> Any:
        _ = table_data
        _ = table_classification
        return None

    @abstractmethod
    def map_table_result(
        self,
        *,
        _table_data: dict[str, Any],
        table_classification: Any,
        _table_pipeline: Any,
    ) -> dict[str, Any] | None:
        """Transform a parsed table into a domain record (or skip with None)."""

    def parse_row(
        self,
        *,
        table_data: dict[str, Any],
        table_classification: Any,
        table_pipeline: Any,
    ) -> dict[str, Any] | None:
        params = inspect.signature(self.map_table_result).parameters
        uses_legacy_names = "_table_data" in params or "_table_pipeline" in params

        kwargs: dict[str, Any] = {
            "table_classification": table_classification,
        }
        if uses_legacy_names:
            kwargs["_table_data"] = table_data
            kwargs["_table_pipeline"] = table_pipeline
        else:
            kwargs["table_data"] = table_data
            kwargs["table_pipeline"] = table_pipeline

        return self.map_table_result(**kwargs)

    def build_result(self, records: list[dict[str, Any]]) -> SectionParseResult:
        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=records,
            parser=self.__class__.__name__,
            source=self._source,
            extras=self._metadata_extras,
        )
