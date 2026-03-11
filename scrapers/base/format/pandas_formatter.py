from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: "ScrapeResult") -> Any:
        import pandas as pd
        from scrapers.base.format.formatter_helpers import extract_data

        return pd.DataFrame(extract_data(result))
