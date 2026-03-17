from __future__ import annotations

from scrapers.base.sections.entry_factory import SectionEntrySpec
from scrapers.base.sections.entry_factory import section_entries_from_specs
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.constructors.sections.championship_results import (
    ConstructorChampionshipResultsSectionParser,
)
from scrapers.constructors.sections.complete_f1_results import (
    ConstructorCompleteF1ResultsSectionParser,
)
from scrapers.constructors.sections.history import ConstructorHistorySectionParser


def constructor_section_entries() -> list[SectionAdapterEntry]:
    specs = [
        SectionEntrySpec(
            section_id="history",
            aliases=("History",),
            parser_factory=ConstructorHistorySectionParser,
        ),
        SectionEntrySpec(
            section_id="championship_results",
            aliases=(
                "Championship_results",
                "Formula_One/World_Championship_results",
            ),
            parser_factory=ConstructorChampionshipResultsSectionParser,
        ),
        SectionEntrySpec(
            section_id="complete_formula_one_results",
            aliases=(
                "Complete_Formula_One_results",
                "Complete_World_Championship_results",
            ),
            parser_factory=ConstructorCompleteF1ResultsSectionParser,
        ),
    ]
    return section_entries_from_specs(domain="constructors", specs=specs)
