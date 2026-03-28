from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Protocol

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SectionParserInput:
    """Unified input contract for section parsers."""

    section_fragment: BeautifulSoup


@dataclass(frozen=True)
class SectionParserConfig:
    """Minimal metadata contract for output mapping."""

    section_id: str
    section_label: str
    parser_name: str
    source: str = "wikipedia"
    metadata_extras: dict[str, object] | None = None


class LegacySectionParser(Protocol):
    """Legacy parser shape: parse(BeautifulSoup) -> records/result."""

    def parse(self, section_fragment: BeautifulSoup) -> object: ...


class LegacySectionParserAdapter:
    """Wrap legacy list-based section parser with explicit output metadata."""

    def __init__(
        self,
        *,
        parser: LegacySectionParser,
        config: SectionParserConfig,
    ) -> None:
        self._parser = parser
        self._config = config

    def parse(self, parser_input: SectionParserInput) -> SectionParseResult:
        raw_result = self._parser.parse(parser_input.section_fragment)
        if isinstance(raw_result, SectionParseResult):
            return raw_result
        if not isinstance(raw_result, list):
            msg = (
                "LegacySectionParserAdapter expected list[dict] or SectionParseResult, "
                f"got {type(raw_result).__name__}."
            )
            raise TypeError(msg)
        records = [record for record in raw_result if isinstance(record, dict)]
        return map_to_section_result(config=self._config, records=records)


def map_to_section_result(
    *,
    config: SectionParserConfig,
    records: list[dict[str, object]],
) -> SectionParseResult:
    return SectionParseResult(
        section_id=config.section_id,
        section_label=config.section_label,
        records=records,
        metadata=build_section_metadata(
            parser=config.parser_name,
            source=config.source,
            extras=config.metadata_extras,
        ),
    )


def parse_with_contract(
    parser: LegacySectionParser,
    parser_input: SectionParserInput,
) -> SectionParseResult:
    raw_result = parser.parse(parser_input.section_fragment)
    if isinstance(raw_result, SectionParseResult):
        return raw_result
    if isinstance(raw_result, list):
        normalized_records: list[dict[str, object]] = []
        for record in raw_result:
            if isinstance(record, dict):
                normalized_records.append(record)
        return SectionParseResult(
            section_id="unknown",
            section_label="unknown",
            records=normalized_records,
            metadata=build_section_metadata(
                parser=parser.__class__.__name__,
                source="legacy",
            ),
        )
    msg = (
        "Unsupported legacy section parser output. Expected SectionParseResult "
        f"or list[dict], got {type(raw_result).__name__}."
    )
    raise TypeError(msg)
