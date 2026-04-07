# ruff: noqa: E501, PLR2004
import warnings

import pytest

from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter, _validate_dataframe_columns


def test_validate_dataframe_columns_raises_for_object_without_columns() -> None:
    # Lines 13-14
    class _NoCols:
        pass

    with pytest.raises(AttributeError, match="columns"):
        _validate_dataframe_columns(_NoCols())


def test_validate_dataframe_columns_passes_for_object_with_columns() -> None:
    class _WithCols:
        columns = ["a", "b"]

    # Should not raise
    _validate_dataframe_columns(_WithCols())


def test_pandas_formatter_returns_dataframe_when_pandas_available() -> None:
    pytest.importorskip("pandas")
    result = PandasDataFrameFormatter.format([{"a": 1, "b": 2}])
    assert hasattr(result, "columns")
    assert list(result.columns) == ["a", "b"]


def test_pandas_formatter_falls_back_to_list_when_no_columns_attr() -> None:
    # Lines 27-29: AttributeError path
    pytest.importorskip("pandas")
    import pandas as pd

    class _BadDataFrame:
        pass

    original_df = pd.DataFrame
    pd.DataFrame = lambda *a, **kw: _BadDataFrame()

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = PandasDataFrameFormatter.format([{"x": 1}])
            assert any(issubclass(warning.category, RuntimeWarning) for warning in w)
        assert result == [{"x": 1}]
    finally:
        pd.DataFrame = original_df
