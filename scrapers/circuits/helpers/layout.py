from typing import Optional

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_wiki_text


def layout_from_spanning_header(
    cells: list[Tag],
    headers: list[str],
) -> Optional[str]:
    if len(cells) != 1 or cells[0].name != "th":
        return None

    th = cells[0]
    try:
        colspan = int(th.get("colspan", "1"))
    except ValueError:
        colspan = 1

    text = clean_wiki_text(th.get_text(strip=True))
    if not text:
        return None

    keywords = (
        "circuit",
        "layout",
        "course",
        "km",
        "mi",
        "present",
        "configuration",
    )

    if colspan >= len(headers) or any(kw in text.lower() for kw in keywords):
        return text

    return None


def detect_layout_name(table: Tag, headers: list[str]) -> Optional[str]:
    caption = table.find("caption")
    if caption:
        txt = clean_wiki_text(caption.get_text(strip=True))
        if txt:
            return txt

    prev = table
    while prev:
        prev = prev.previous_sibling
        if not isinstance(prev, Tag):
            continue
        if prev.name in {"h2", "h3", "h4"}:
            txt = clean_wiki_text(prev.get_text(strip=True))
            if txt:
                return txt

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        layout = layout_from_spanning_header(cells, headers)
        if layout:
            return layout

    return None
