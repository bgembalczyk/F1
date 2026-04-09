from scrapers.constructors.constructors_sections.adapter import constructor_section_entries
from scrapers.constructors.constructors_sections.championship_results import (
    ConstructorChampionshipResultsSectionParser,
)
from scrapers.constructors.constructors_sections.common import ConstructorTablesSectionParser
from scrapers.constructors.constructors_sections.complete_f1_results import (
    ConstructorCompleteF1ResultsSectionParser,
)
from scrapers.constructors.constructors_sections.history import ConstructorHistorySectionParser
from scrapers.constructors.constructors_sections.list_section import ConstructorsSectionParser
from scrapers.constructors.constructors_sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.constructors_sections.list_section import CurrentConstructorsTableParser
from scrapers.constructors.constructors_sections.list_section import FormerConstructorsSectionParser
from scrapers.constructors.constructors_sections.list_section import FormerConstructorsTableParser
from scrapers.constructors.constructors_sections.list_section import (
    IndianapolisConstructorsListParser,
)
from scrapers.constructors.constructors_sections.list_section import IndianapolisOnlySubSectionParser

__all__ = [
    "constructor_section_entries",
    "ConstructorChampionshipResultsSectionParser",
    "ConstructorTablesSectionParser",
    "ConstructorCompleteF1ResultsSectionParser",
    "ConstructorHistorySectionParser",
    "IndianapolisConstructorsListParser",
    "IndianapolisOnlySubSectionParser",
    "CurrentConstructorsTableParser",
    "FormerConstructorsTableParser",
    "ConstructorsSectionParser",
    "CurrentConstructorsSectionParser",
    "FormerConstructorsSectionParser",
]
