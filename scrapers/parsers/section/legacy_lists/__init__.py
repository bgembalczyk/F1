from scrapers.parsers.section.legacy_lists.fatalities import DetailByDriverSubSectionParser
from scrapers.parsers.section.legacy_lists.fatalities import FatalitiesSectionParser
from scrapers.parsers.section.legacy_lists.fatalities import FatalitiesTableMapper
from scrapers.parsers.section.legacy_lists.female_drivers import DriversSectionParser
from scrapers.parsers.section.legacy_lists.female_drivers import FemaleDriversTableMapper
from scrapers.parsers.section.legacy_lists.female_drivers import OfficialDriversSubSectionParser
from scrapers.parsers.section.legacy_lists.grands_prix import ByRaceTitleSubSectionParser
from scrapers.parsers.section.legacy_lists.grands_prix import GrandsPrixTableMapper
from scrapers.parsers.section.legacy_lists.grands_prix import RacesSectionParser
from scrapers.parsers.section.legacy_lists.tyres import ManufacturersSectionParser
from scrapers.parsers.section.legacy_lists.tyres import TyreManufacturersBySeasonSubSectionParser
from scrapers.parsers.section.legacy_lists.tyres import TyreManufacturersBySeasonTableMapper

__all__ = [
    "ByRaceTitleSubSectionParser",
    "DetailByDriverSubSectionParser",
    "DriversSectionParser",
    "FatalitiesSectionParser",
    "FatalitiesTableMapper",
    "FemaleDriversTableMapper",
    "GrandsPrixTableMapper",
    "ManufacturersSectionParser",
    "OfficialDriversSubSectionParser",
    "RacesSectionParser",
    "TyreManufacturersBySeasonSubSectionParser",
    "TyreManufacturersBySeasonTableMapper",
]
