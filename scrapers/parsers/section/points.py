from __future__ import annotations

from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.table.points import PointsScoringSystemsHistoryTableMapper
from scrapers.parsers.table.points import ShortenedRacesPointsTableMapper
from scrapers.parsers.table.points import SprintPointsTableMapper
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser
from scrapers.parsers.wiki.sublevels.sub_sub_section import SubSubSectionParser


class SprintRacesSubSubSectionParser(ApplyForElementsMixin, SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SprintPointsTableMapper()

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        if not parsed.get("sub_sub_sub_sections"):
            parsed = self.child_parser.parse(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed


class ShortenedRacesSubSubSectionParser(ApplyForElementsMixin, SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = ShortenedRacesPointsTableMapper()

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed


class SpecialCasesSubSubSectionRouter(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.sprint_parser = SprintRacesSubSubSectionParser()
        self.shortened_parser = ShortenedRacesSubSubSectionParser()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        section_id = getattr(context, "section_id", "") or ""
        if "sprint" in section_id.lower():
            return self.sprint_parser.parse(elements, context=context)
        if "shortened" in section_id.lower():
            return self.shortened_parser.parse(elements, context=context)
        parsed = super()._parse_group(elements, context=context)
        self.sprint_parser.apply_table_mapper(parsed)
        self.shortened_parser.apply_table_mapper(parsed)
        return parsed


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSubSectionRouter()


class PointsScoringSystemsSectionParser(ApplyForElementsMixin, NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSectionParser()
        self._table_parser = PointsScoringSystemsHistoryTableMapper()

    @property
    def sprint_subsection_parser(self) -> SprintRacesSubSubSectionParser:
        router = self.child_parser.child_parser  # type: ignore[union-attr]
        return router.sprint_parser  # type: ignore[union-attr]

    @property
    def shortened_subsection_parser(self) -> ShortenedRacesSubSubSectionParser:
        router = self.child_parser.child_parser  # type: ignore[union-attr]
        return router.shortened_parser  # type: ignore[union-attr]

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self.apply_table_mapper(parsed)
        return parsed
