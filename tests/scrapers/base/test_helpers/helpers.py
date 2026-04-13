from bs4 import BeautifulSoup

from scrapers.columns.context import ColumnContext


def soup_with_catlinks(links: list[str]) -> BeautifulSoup:
    li_items = "".join(f'<li><a href="/wiki/{t}">{t}</a></li>' for t in links)
    html = f'<div id="mw-normal-catlinks"><ul>{li_items}</ul></div>'
    return BeautifulSoup(html, "html.parser")


def soup_no_catlinks() -> BeautifulSoup:
    return BeautifulSoup("<div>no cats here</div>", "html.parser")


def table_func(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    assert table is not None
    return table


def ctx(clean_text: str | None, raw_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Date",
        key="date",
        raw_text=raw_text if raw_text is not None else clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


