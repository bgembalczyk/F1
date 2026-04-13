from dataclasses import dataclass

from scrapers.infobox.extraction.extractor import InfoboxLinkExtractor
from scrapers.infobox.section.collector import InfoboxSectionCollector
from scrapers.parsers.infobox.driver_cell import InfoboxCellValueExtractor
from scrapers.parsers.infobox.field.career import InfoboxCareerParser
from scrapers.parsers.infobox.field.title import InfoboxTitlesParser
from scrapers.parsers.infobox.general import InfoboxGeneralExtractor


@dataclass(frozen=True)
class DriverInfoboxBundle:
    link_extractor: InfoboxLinkExtractor
    cell_extractor: InfoboxCellValueExtractor
    general_extractor: InfoboxGeneralExtractor
    titles_parser: InfoboxTitlesParser
    career_parser: InfoboxCareerParser
    section_discovery: InfoboxSectionCollector
