from typing import Any, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: ScrapeResult) -> Any:
        from scrapers.base.format.formatter_helpers import extract_data

        return pd.DataFrame(extract_data(result))
