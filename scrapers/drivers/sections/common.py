from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.drivers.sections.results import DriverResultsSectionParser


@dataclass(frozen=True)
class DriverResultsSectionConfig:
    section_id: str
    section_label: str
    header_aliases: tuple[str, ...]


class BaseDriverResultsSectionParser:
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

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        parsed = self._parser.parse(section_fragment)
        return SectionParseResult(
            section_id=self._section_id,
            section_label=self._section_label,
            records=parsed.records,
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia", extras={"aliases": self._header_aliases}),
        )
