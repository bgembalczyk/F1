from __future__ import annotations

from typing import Any

from scrapers.parsers.parse_result import ParseMetadata
from scrapers.parsers.parse_result import ParseResult
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result


class LegacyParseResultAdapter:
    @staticmethod
    def from_section(result: SectionParseResult) -> ParseResult[list[dict[str, Any]]]:
        metadata = dict(result.metadata)
        return ParseResult(
            payload=list(result.records),
            metadata=ParseMetadata(
                parser=str(metadata.get("parser", "unknown_parser")),
                source=str(metadata.get("source", "unknown_source")),
                extras={
                    key: value
                    for key, value in metadata.items()
                    if key not in {"parser", "source"}
                },
            ),
        )

    @staticmethod
    def to_section(
        *,
        parse_result: ParseResult[list[dict[str, Any]]],
        section_id: str,
        section_label: str,
    ) -> SectionParseResult:
        return build_section_parse_result(
            section_id=section_id,
            section_label=section_label,
            records=parse_result.payload,
            parser=parse_result.metadata.parser,
            source=parse_result.metadata.source,
            extras=parse_result.metadata.extras,
        )

    @staticmethod
    def from_table(result: dict[str, Any]) -> ParseResult[list[dict[str, Any]]]:
        return ParseResult(
            payload=list(result.get("domain_rows", [])),
            metadata=ParseMetadata(
                parser=str(result.get("table_type", "wiki_table")),
                source="wikipedia",
                extras={
                    "domain_column_map": result.get("domain_column_map", {}),
                    "missing_columns_policy": result.get("missing_columns_policy", "skip"),
                    "extra_columns_policy": result.get("extra_columns_policy", "ignore"),
                },
            ),
        )

    @staticmethod
    def from_infobox(result: dict[str, Any]) -> ParseResult[dict[str, Any]]:
        return ParseResult(
            payload=result,
            metadata=ParseMetadata(
                parser="InfoboxHtmlParser",
                source="wikipedia",
                extras={"title": result.get("title")},
            ),
        )


__all__ = ["LegacyParseResultAdapter"]
