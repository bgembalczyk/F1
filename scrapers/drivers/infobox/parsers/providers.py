from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from scrapers.drivers.infobox.parsers.career import InfoboxCareerParser
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.general import InfoboxGeneralParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.section_collector import InfoboxSectionCollector
from scrapers.drivers.infobox.parsers.title import InfoboxTitlesParser


class InfoboxSectionDiscovery(Protocol):
    def collect(self, table: object) -> list[dict[str, object]]: ...


@dataclass(frozen=True)
class DriverInfoboxParserBundle:
    link_extractor: InfoboxLinkExtractor
    cell_parser: InfoboxCellParser
    general_parser: InfoboxGeneralParser
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionDiscovery


class DriverInfoboxParserProvider(Protocol):
    def build(self, *, include_urls: bool, wikipedia_base: str, schema: object, logger: object) -> DriverInfoboxParserBundle: ...


class DefaultDriverInfoboxParserProvider:
    def __init__(
        self,
        *,
        section_discovery: InfoboxSectionDiscovery | None = None,
    ) -> None:
        self._section_discovery = section_discovery or InfoboxSectionCollector()

    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxParserBundle:
        link_extractor = InfoboxLinkExtractor(
            include_urls=include_urls,
            wikipedia_base=wikipedia_base,
        )
        cell_parser = InfoboxCellParser(
            include_urls=include_urls,
            link_extractor=link_extractor,
        )
        general_parser = InfoboxGeneralParser(
            include_urls=include_urls,
            link_extractor=link_extractor,
            schema=schema,
            logger=logger,
        )
        titles_parser = InfoboxTitlesParser(link_extractor)
        career_parser = InfoboxCareerParser(cell_parser)
        return DriverInfoboxParserBundle(
            link_extractor=link_extractor,
            cell_parser=cell_parser,
            general_parser=general_parser,
            titles_parser=titles_parser,
            career_parser=career_parser,
            section_discovery=self._section_discovery,
        )
