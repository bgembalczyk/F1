from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn

EXPECTED_ENTRIES = 12
EXPECTED_STARTS = 10
EXPECTED_FRACTIONAL_POINTS = 0.5
EXPECTED_CHAMPIONSHIP_POINTS = 42.0
POINTS_TOLERANCE = 1e-9


def _ctx(
    raw_text: str,
    *,
    clean_text: str | None = None,
    links: list[dict] | None = None,
    model_fields: set[str] | None = None,
) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=links or [],
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=model_fields,
    )


def _ctx_with_cell(html: str) -> ColumnContext:
    cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    raw_text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Points",
        key="points",
        raw_text=raw_text,
        clean_text=raw_text,
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_driver_name_status_column_apply() -> None:
    column = DriverNameStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("Jane Doe*"), record)

    assert record["driver"] == {"text": "Jane Doe", "url": None}
    assert record["is_active"] is True
    assert record["is_world_champion"] is False


def test_driver_name_status_column_active_champion() -> None:
    column = DriverNameStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("John Doe~"), record)

    assert record["is_active"] is True
    assert record["is_world_champion"] is True


def test_entries_starts_column_apply() -> None:
    column = EntriesStartsColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("12 (10)"), record)

    assert record["entries"] == EXPECTED_ENTRIES
    assert record["starts"] == EXPECTED_STARTS


def test_fatality_date_column_parse() -> None:
    column = FatalityDateColumn()
    parsed = column.parse(_ctx("11 June 1950#"))

    assert parsed["date"] == "1950-06-11"
    assert parsed["formula_category"] == "F2"


def test_fatality_event_column_parse() -> None:
    column = FatalityEventColumn()
    parsed = column.parse(_ctx("1958 French Grand Prix†"))

    assert parsed["event"] == "1958 French Grand Prix"
    assert parsed["championship"] is False


def test_points_column_hidden_span_zero() -> None:
    column = PointsColumn()
    parsed = column.parse(_ctx_with_cell('<span style="display:none">4</span>0'))
    assert parsed == 0.0


def test_points_column_hidden_span_fraction() -> None:
    column = PointsColumn()
    parsed = column.parse(_ctx_with_cell('<span style="display:none">5</span>0.5'))
    assert parsed == EXPECTED_FRACTIONAL_POINTS


def test_points_column_hidden_span_dash() -> None:
    column = PointsColumn()
    parsed = column.parse(_ctx_with_cell('<span style="display:none">2</span>-'))
    assert parsed is None


def test_points_column_frac_span_mixed_number() -> None:
    """Total points expressed as a mixed number using Wikipedia frac template."""
    column = PointsColumn()
    html = (
        '<b>42 (<style data-mw-deduplicate="TemplateStyles:r1154941027">'
        ".mw-parser-output .frac{white-space:nowrap}"
        "</style>"
        '<span class="frac">57'
        '<span class="sr-only">+</span>'
        '<span class="num">1</span>\u2044'
        '<span class="den">7</span>'
        "</span>)</b>"
    )
    parsed = column.parse(_ctx_with_cell(html))
    assert isinstance(parsed, dict)
    assert parsed["championship_points"] == EXPECTED_CHAMPIONSHIP_POINTS
    assert abs(parsed["total_points"] - (57 + 1 / 7)) < POINTS_TOLERANCE
