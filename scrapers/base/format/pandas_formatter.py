from __future__ import annotations

from typing import Any

import pandas as pd

from scrapers.base.format.formatter_helpers import _extract_data
from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    def format(self, result: ScrapeResult) -> Any:
        return pd.DataFrame(_extract_data(result))
