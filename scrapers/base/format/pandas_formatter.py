from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: "ScrapeResult") -> Any:
        # di-antipattern-allow: optional dependency imported lazily to keep pandas optional.
        import pandas as pd

        # di-antipattern-allow: lightweight lazy import aligned with optional pandas path.
        from scrapers.base.format.formatter_helpers import extract_data

        return pd.DataFrame(extract_data(result))
