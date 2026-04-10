from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.helpers.constants import POINTS_WITH_TOTAL_RE
from scrapers.columns.helpers.results_parsing import ResultsParsingHelpers
from scrapers.parsers.helpers import extract_visible_text


class PointsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        text = extract_visible_text(ctx).strip()
        if not text:
            return None

        match = POINTS_WITH_TOTAL_RE.search(text)
        if match:
            main_text = match.group(1).strip()
            total_text = match.group(2).strip()
            return {
                "championship_points": ResultsParsingHelpers.parse_points_value(
                    main_text,
                ),
                "total_points": ResultsParsingHelpers.parse_points_value(total_text),
            }

        return ResultsParsingHelpers.parse_points_value(text)


__all__ = ["PointsColumn"]
