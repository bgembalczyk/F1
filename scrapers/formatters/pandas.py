import warnings
from typing import TYPE_CHECKING
from typing import Any

import pandas as pd

from scrapers.formatters.helpers import extract_data
from scrapers.results import ScrapeResult


def validate_dataframe_columns(dataframe: Any) -> None:
    if not hasattr(dataframe, "columns"):
        msg = "Pandas DataFrame stub does not expose 'columns'."
        raise AttributeError(msg)


class PandasDataFrameFormatter:
    @staticmethod
    def format(result: ScrapeResult) -> Any:
        data = extract_data(result)
        try:

            dataframe = pd.DataFrame(data)
            validate_dataframe_columns(dataframe)
        except (ImportError, AttributeError):
            warnings.warn("Pandas nie jest zainstalowane", RuntimeWarning, stacklevel=2)
            return data
        else:
            return dataframe
