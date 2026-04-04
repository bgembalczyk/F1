from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.format.formatter_helpers import extract_data

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: "ScrapeResult") -> Any:
        # di-antipattern-allow: optional dependency.
        import pandas as pd  # noqa: PLC0415

        return pd.DataFrame(extract_data(result))
