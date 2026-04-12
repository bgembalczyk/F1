from dataclasses import dataclass

from scrapers.infobox.extraction.extractor import InfoboxLinkExtractor
from scrapers.infobox.section.discovery import InfoboxSectionDiscovery
from scrapers.parsers.infobox.driver_cell import InfoboxCellParser
from scrapers.parsers.infobox.field.career import InfoboxCareerParser
from scrapers.parsers.infobox.field.title import InfoboxTitlesParser
from scrapers.parsers.infobox.general import InfoboxGeneralParser
from scrapers.parsers.contracts.bundles import ParsingBundle


@dataclass(frozen=True)
class DriverInfoboxBundle(ParsingBundle):
    link_extractor: InfoboxLinkExtractor
    cell_parser: InfoboxCellParser
    general_parser: InfoboxGeneralParser
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionDiscovery

