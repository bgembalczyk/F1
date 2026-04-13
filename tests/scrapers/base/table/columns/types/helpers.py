from bs4 import BeautifulSoup

from scrapers.columns.context import ColumnContext
from scrapers.sentinels_table import SKIP_SENTINEL


def ctx_time(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Time",
        key="time",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def ctx_restart(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="R",
        key="restart_status",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )

def ctx_position(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Pos",
        key="position",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def context_multi(clean_text: str | None, raw_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Multi",
        key="multi",
        raw_text=raw_text or clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
        skip_sentinel=SKIP_SENTINEL,
    )


def ctx_list(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Items",
        key="items",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def ctx_links(
    *,
    clean_text: str,
    links: list[dict[str, str | None]] | None = None,
    html: str | None = None,
) -> ColumnContext:
    cell = None
    if html is not None:
        cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Links",
        key="links",
        raw_text=clean_text,
        clean_text=clean_text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def ctx_constructor(
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


def ctx_br(
    *,
    html: str | None = None,
    clean_text: str = "",
    raw_text: str | None = None,
) -> ColumnContext:
    cell = None
    if html is not None:
        cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Items",
        key="items",
        raw_text=raw_text,
        clean_text=clean_text,
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


