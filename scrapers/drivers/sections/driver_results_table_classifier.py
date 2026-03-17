from __future__ import annotations

from scrapers.drivers.sections.driver_results_constants import (
    CAREER_HIGHLIGHTS_REQUIRED_HEADERS,
)
from scrapers.drivers.sections.driver_results_constants import (
    CAREER_SUMMARY_REQUIRED_HEADERS,
)
from scrapers.drivers.sections.driver_results_constants import (
    COMPLETE_RESULTS_REQUIRED_HEADER,
)


class DriverResultsTableClassifier:
    def classify(self, headers: list[str]) -> str | None:
        if not headers:
            return None

        header_set = set(headers)
        if CAREER_HIGHLIGHTS_REQUIRED_HEADERS.issubset(header_set):
            return "career_highlights"
        if CAREER_SUMMARY_REQUIRED_HEADERS.issubset(header_set):
            return "career_summary"
        if COMPLETE_RESULTS_REQUIRED_HEADER in header_set:
            return "complete_results"
        return None
