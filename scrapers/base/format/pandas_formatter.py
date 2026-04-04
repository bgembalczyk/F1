import warnings
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.format.formatter_helpers import extract_data

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: "ScrapeResult") -> Any:
        data = extract_data(result)
        try:
            # di-antipattern-allow: optional dependency.
            import pandas as pd

            return pd.DataFrame(data)
        except (ImportError, AttributeError):
            warnings.warn("Pandas nie jest zainstalowane", RuntimeWarning, stacklevel=2)
            return data
