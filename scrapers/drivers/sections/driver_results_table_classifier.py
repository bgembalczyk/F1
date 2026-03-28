from __future__ import annotations

from models.value_objects.enums import TableType
from scrapers.drivers.sections.constants import CAREER_HIGHLIGHTS_REQUIRED_HEADERS
from scrapers.drivers.sections.constants import CAREER_SUMMARY_REQUIRED_HEADERS
from scrapers.drivers.sections.constants import COMPLETE_RESULTS_REQUIRED_HEADER


class DriverResultsTableClassifier:
    def classify(self, headers: list[str]) -> TableType | None:
        if not headers:
            return None

        header_set = set(headers)
        if CAREER_HIGHLIGHTS_REQUIRED_HEADERS.issubset(header_set):
            return TableType.CAREER_HIGHLIGHTS
        if CAREER_SUMMARY_REQUIRED_HEADERS.issubset(header_set):
            return TableType.CAREER_SUMMARY
        if COMPLETE_RESULTS_REQUIRED_HEADER in header_set:
            return TableType.COMPLETE_RESULTS
        return None
