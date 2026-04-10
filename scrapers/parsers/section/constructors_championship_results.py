from __future__ import annotations

from scrapers.sections.common_constructors import ConstructorTablesSectionParser


class ConstructorChampionshipResultsSectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="championship_results",
            section_label="Championship results",
        )


__all__ = ["ConstructorChampionshipResultsSectionParser"]
