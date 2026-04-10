from __future__ import annotations

from scrapers.parsers.section.table.constructors import ConstructorTablesSectionParser


class ConstructorHistorySectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(section_id="history", section_label="History")


__all__ = ["ConstructorHistorySectionParser"]
