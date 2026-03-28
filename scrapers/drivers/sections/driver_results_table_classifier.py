from __future__ import annotations

from scrapers.drivers.sections.constants import CAREER_HIGHLIGHTS_REQUIRED_HEADERS
from scrapers.drivers.sections.constants import CAREER_SUMMARY_REQUIRED_HEADERS
from scrapers.drivers.sections.constants import COMPLETE_RESULTS_REQUIRED_HEADER


class DriverResultsTableClassifier:
    _RULES: tuple[tuple[str, frozenset[str] | str], ...] = (
        ("career_highlights", CAREER_HIGHLIGHTS_REQUIRED_HEADERS),
        ("career_summary", CAREER_SUMMARY_REQUIRED_HEADERS),
        ("complete_results", COMPLETE_RESULTS_REQUIRED_HEADER),
    )

    def classify(self, headers: list[str]) -> str | None:
        if not headers:
            return None

        header_set = set(headers)
        for table_type, matcher in self._RULES:
            if isinstance(matcher, str):
                if matcher in header_set:
                    return table_type
                continue
            if matcher.issubset(header_set):
                return table_type
        return None
