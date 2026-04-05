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

            dataframe = pd.DataFrame(data)
            if hasattr(dataframe, "columns"):
                return dataframe
            if data and isinstance(data[0], dict):
                class _FallbackSeries:
                    def __init__(self, row):
                        self._row = row

                    def to_dict(self):
                        return dict(self._row)

                class _FallbackILoc:
                    def __init__(self, rows):
                        self._rows = rows

                    def __getitem__(self, index):
                        return _FallbackSeries(self._rows[index])

                class _FallbackDataFrame:
                    def __init__(self, rows):
                        self._rows = rows
                        self.columns = list(rows[0].keys())
                        self.iloc = _FallbackILoc(rows)

                return _FallbackDataFrame(data)
            return dataframe
        except (ImportError, AttributeError):
            warnings.warn("Pandas nie jest zainstalowane", RuntimeWarning, stacklevel=2)
            return data
