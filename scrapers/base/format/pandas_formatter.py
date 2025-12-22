from __future__ import annotations

from typing import Any

import pandas as pd

from scrapers.base.format.formatter_helpers import extract_data
from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: ScrapeResult) -> Any:
        return pd.DataFrame(extract_data(result))
