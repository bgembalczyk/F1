from dataclasses import dataclass

from scrapers.infobox.parsers.drivers.career import InfoboxCareerParser
from scrapers.infobox.parsers.drivers.cell import InfoboxCellParser
from scrapers.infobox.parsers.drivers.general import InfoboxGeneralParser
from scrapers.infobox.parsers.drivers.link_extractor import InfoboxLinkExtractor
from scrapers.infobox.parsers.drivers.title import InfoboxTitlesParser
from scrapers.infobox.section_discovery import InfoboxSectionDiscovery
from scrapers.parsers.roles import ParserBundle


@dataclass(frozen=True)
class DriverInfoboxParserBundle(ParserBundle):
    link_extractor: InfoboxLinkExtractor
    cell_parser: InfoboxCellParser
    general_parser: InfoboxGeneralParser
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionDiscovery
