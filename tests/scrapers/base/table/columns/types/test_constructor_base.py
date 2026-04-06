from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.constructor_base import BaseConstructorColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class _ContractConstructorColumn(BaseConstructorColumn):
    part_parser_cls = ConstructorPartColumn


def _ctx(
    *,
    clean_text: str,
    links: list[dict[str, str | None]] | None = None,
    html: str | None = None,
) -> ColumnContext:
    cell = None
    if html is not None:
        cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Constructor",
        key="constructor",
        raw_text=clean_text,
        clean_text=clean_text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_constructor_base_parses_single_line_text_without_links() -> None:
    parsed = _ContractConstructorColumn().parse(
        _ctx(clean_text="Ferrari - Renault"),
    )

    assert parsed == {
        "chassis_constructor": {"text": "Ferrari", "url": None},
        "engine_constructor": {"text": "Renault", "url": None},
    }


def test_constructor_base_parses_multiline_cell_into_list() -> None:
    parsed = _ContractConstructorColumn().parse(
        _ctx(
            clean_text="Ferrari - Renault McLaren - Mercedes",
            html=(
                "<a href='/wiki/Ferrari'>Ferrari</a>"
                " - <a href='/wiki/Renault'>Renault</a>"
                "<br>"
                "<a href='/wiki/McLaren'>McLaren</a>"
                " - <a href='/wiki/Mercedes'>Mercedes</a>"
            ),
            links=[
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
                {"text": "Renault", "url": "/wiki/Renault"},
                {"text": "McLaren", "url": "/wiki/McLaren"},
                {"text": "Mercedes", "url": "/wiki/Mercedes"},
            ],
        ),
    )

    assert parsed == [
        {
            "chassis_constructor": {"text": "Ferrari", "url": "/wiki/Ferrari"},
            "engine_constructor": {"text": "Renault", "url": "/wiki/Renault"},
        },
        {
            "chassis_constructor": {"text": "McLaren", "url": "/wiki/McLaren"},
            "engine_constructor": {"text": "Mercedes", "url": "/wiki/Mercedes"},
        },
    ]


def test_constructor_base_returns_none_for_empty_values() -> None:
    parsed = _ContractConstructorColumn().parse(_ctx(clean_text=""))

    assert parsed is None


def test_constructor_base_preserves_duplicate_links() -> None:
    parsed = _ContractConstructorColumn().parse(
        _ctx(
            clean_text="Ferrari - Ferrari",
            links=[
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
            ],
        ),
    )

    assert parsed == {
        "chassis_constructor": {"text": "Ferrari", "url": "/wiki/Ferrari"},
        "engine_constructor": {"text": "Ferrari", "url": "/wiki/Ferrari"},
    }


def test_constructor_base_supports_nonstandard_separator_with_links() -> None:
    parsed = _ContractConstructorColumn().parse(
        _ctx(
            clean_text="Ferrari / Renault",
            links=[
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
                {"text": "Renault", "url": "/wiki/Renault"},
            ],
        ),
    )

    assert parsed == {
        "chassis_constructor": {"text": "Ferrari", "url": "/wiki/Ferrari"},
        "engine_constructor": {"text": "Renault", "url": "/wiki/Renault"},
    }


def test_constructor_base_is_idempotent_for_same_context() -> None:
    column = _ContractConstructorColumn()
    ctx = _ctx(
        clean_text="Ferrari - Renault",
        links=[
            {"text": "Ferrari", "url": "/wiki/Ferrari"},
            {"text": "Renault", "url": "/wiki/Renault"},
        ],
    )

    first = column.parse(ctx)
    second = column.parse(ctx)

    assert first == second
