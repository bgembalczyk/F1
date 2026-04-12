from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.columns.types.function.circuit_location import LocationColumn


def ctx(
    *,
    clean_text: str | None,
    links: list[dict[str, str | None]],
) -> ColumnContext:
    return ColumnContext(
        header="Location",
        key="location",
        raw_text=clean_text,
        clean_text=clean_text,
        links=links,
        cell=None,
        base_url="https://example.com",
    )


def test_parse_location_returns_none_for_empty_text_and_links() -> None:
    column = LocationColumn()

    assert column.parse(ctx(clean_text="", links=[])) is None


def test_parse_location_with_link_and_layout_suffix() -> None:
    column = LocationColumn()

    parsed = column.parse(
        ctx(
            clean_text="Silverstone Circuit (Grand Prix layout)",
            links=[{"text": "Silverstone Circuit", "url": "/wiki/Silverstone_Circuit"}],
        ),
    )

    assert parsed == {
        "circuit": {
            "text": "Silverstone Circuit",
            "url": "/wiki/Silverstone_Circuit",
        },
        "layout": "Grand Prix layout",
    }


def test_parse_location_without_links_uses_clean_text_as_circuit() -> None:
    column = LocationColumn()

    parsed = column.parse(ctx(clean_text="Monaco", links=[]))

    assert parsed == {"circuit": {"text": "Monaco", "url": None}}
