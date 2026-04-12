from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.parsers.section.table.driver_results import DriverResultsSectionParser
from scrapers.parsers.wiki.base_section_parser import BaseSectionParser
from scrapers.section.config.driver_results import DriverResultsSectionConfig
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class BaseDriverResultsSectionParser(BaseSectionParser):
    def __init__(
        self,
        *,
        parser: DriverResultsSectionParser,
        section_id: str,
        section_label: str,
        header_aliases: tuple[str, ...],
    ) -> None:
        self._parser = parser
        self._section_id = section_id
        self._section_label = section_label
        self._header_aliases = header_aliases

    @classmethod
    def from_config(
        cls,
        *,
        parser: DriverResultsSectionParser,
        config: DriverResultsSectionConfig,
    ) -> BaseDriverResultsSectionParser:
        return cls(
            parser=parser,
            section_id=config.section_id,
            section_label=config.section_label,
            header_aliases=config.header_aliases,
        )

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        parsed = self._parser.parse(fragment)
        return build_section_parse_result(
            section_id=self._section_id,
            section_label=self._section_label,
            records=parsed.records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"aliases": self._header_aliases},
        )


__all__ = [
    "BaseDriverResultsSectionParser",
]
