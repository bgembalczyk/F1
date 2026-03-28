from scrapers.base.table.columns.context import ColumnContext
from scrapers.constructors.columns.constructor import ConstructorColumn


def _ctx_with_links(links: list[dict]) -> ColumnContext:
    return ColumnContext(
        header="Constructor",
        key="constructor",
        raw_text="Mercedes",
        clean_text="Mercedes",
        links=links,
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=None,
    )


def test_constructor_column_single_link_duplicates_engine() -> None:
    """When only one constructor link exists, engine equals chassis."""
    column = ConstructorColumn()
    link = {
        "text": "Mercedes",
        "url": "https://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One",
    }
    result = column.parse(_ctx_with_links([link]))

    assert result["chassis_constructor"] == link
    assert result["engine_constructor"] == link


def test_constructor_column_two_links_distinct() -> None:
    """When two constructor links exist, chassis and engine differ."""
    column = ConstructorColumn()
    chassis_link = {"text": "McLaren", "url": "https://en.wikipedia.org/wiki/McLaren"}
    engine_link = {
        "text": "Honda",
        "url": "https://en.wikipedia.org/wiki/Honda_in_Formula_One",
    }
    result = column.parse(_ctx_with_links([chassis_link, engine_link]))

    assert result["chassis_constructor"] == chassis_link
    assert result["engine_constructor"] == engine_link
