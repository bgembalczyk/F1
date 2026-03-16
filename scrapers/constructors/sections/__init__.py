"""Section parser namespace for constructors domain."""

from .list_section import ConstructorsListSectionParser
from .championship_results import ConstructorChampionshipResultsSectionParser
from .complete_f1_results import ConstructorCompleteF1ResultsSectionParser
from .history import ConstructorHistorySectionParser
from .adapter import constructor_section_entries


__all__ = [
    "ConstructorsListSectionParser",
    "ConstructorHistorySectionParser",
    "ConstructorChampionshipResultsSectionParser",
    "ConstructorCompleteF1ResultsSectionParser",
    "constructor_section_entries",
]
