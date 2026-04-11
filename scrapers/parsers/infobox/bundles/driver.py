from dataclasses import dataclass

from scrapers.infobox.extraction.extractor import InfoboxLinkExtractor
from scrapers.infobox.section.discovery import InfoboxSectionDiscovery
from scrapers.parsers.infobox.drivers.career import InfoboxCareerParser
from scrapers.parsers.infobox.drivers.cell import InfoboxCellParser
from scrapers.parsers.infobox.drivers.title import InfoboxTitlesParser
from scrapers.parsers.infobox.general import InfoboxGeneralParser
from scrapers.parsers.roles import ParserBundle


@dataclass(frozen=True)
class DriverInfoboxParserBundle(ParserBundle):
    link_extractor: InfoboxLinkExtractor
    cell_parser: InfoboxCellParser
    general_parser: InfoboxGeneralParser
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionDiscovery
