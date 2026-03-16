from __future__ import annotations

from scrapers.constructors.sections.common import ConstructorTablesSectionParser


class ConstructorHistorySectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(section_id="History", section_label="History")
