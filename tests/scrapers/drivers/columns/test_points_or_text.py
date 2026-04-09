from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.drivers.drivers_columns.points_or_text import PointsOrTextColumn


def ctx(html: str, clean_text: str) -> ColumnContext:
    cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Points",
        key="points",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
        model_fields=None,
    )


def test_points_or_text_column_returns_numeric_points() -> None:
    column = PointsOrTextColumn()
    assert column.parse(ctx("42", "42")) == 42.0  # noqa: PLR2004


def test_points_or_text_column_returns_text_when_not_numeric() -> None:
    column = PointsOrTextColumn()
    assert column.parse(ctx("Shared drive", "Shared drive")) == "Shared drive"


def test_points_or_text_column_returns_none_for_dash_and_empty() -> None:
    column = PointsOrTextColumn()
    assert column.parse(ctx("-", "-")) is None
    assert column.parse(ctx("", "")) is None
