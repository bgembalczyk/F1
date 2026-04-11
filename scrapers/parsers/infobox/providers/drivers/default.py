from __future__ import annotations

from scrapers.infobox.extraction.extractor.link import InfoboxLinkExtractor
from scrapers.infobox.section.collector import InfoboxSectionCollector
from scrapers.infobox.section.discovery import InfoboxSectionDiscovery
from scrapers.parsers.infobox.bundles.driver import DriverInfoboxParserBundle
from scrapers.parsers.infobox.driver_cell import InfoboxCellParser
from scrapers.parsers.infobox.field.career import InfoboxCareerParser
from scrapers.parsers.infobox.field.title import InfoboxTitlesParser
from scrapers.parsers.infobox.general import InfoboxGeneralParser


class DefaultDriverInfoboxProvider:
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
