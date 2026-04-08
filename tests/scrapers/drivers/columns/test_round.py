from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.drivers.columns.round import RoundColumn


def ctx(html: str, *, links: list[dict] | None = None) -> ColumnContext:
    cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Round",
        key="round",
        raw_text=text,
        clean_text=text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
        model_fields=None,
    )


def test_round_column_parses_numeric_result_and_flags() -> None:
    column = RoundColumn()
    result = column.parse(ctx("<strong>1</strong>"))

    assert result["code"] == "1"
    assert result["result"] == 1
    assert result["pole_position"] is True
    assert result["superscript"] is None


def test_round_column_uses_fallback_code_and_text_result() -> None:
    column = RoundColumn()
    result = column.parse(ctx("Monaco DNS"))

    assert result["round"] is None
    assert result["code"] == "Monaco DNS"
    assert result["result"] == "Monaco DNS"


def test_round_column_returns_none_without_tokens() -> None:
    column = RoundColumn()
    assert column.parse(ctx(" ")) is None
