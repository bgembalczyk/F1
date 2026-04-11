from dataclasses import dataclass

from scrapers.infobox.infobox.drivers.career import InfoboxCareerParser
from scrapers.infobox.infobox.drivers.cell import InfoboxCellParser
from scrapers.infobox.infobox.drivers.general import InfoboxGeneralParser
from scrapers.infobox.infobox.drivers.link_extractor import InfoboxLinkExtractor
from scrapers.infobox.infobox.drivers.title import InfoboxTitlesParser
from scrapers.parsers.roles import ParserBundle
from scrapers.infobox.section_discovery import InfoboxSectionDiscovery


@dataclass(frozen=True)
class DriverInfoboxParserBundle(ParserBundle):
    link_extractor: InfoboxLinkExtractor
    cell_parser: InfoboxCellParser
    general_parser: InfoboxGeneralParser
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionDiscovery
