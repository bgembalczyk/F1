from __future__ import annotations

from typing import Any

from scrapers.helpers.text import strip_marks

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"
RESTART_STATUS_MAP = {
    "N": "race_was_not_restarted",
    "Y": "race_was_restarted_over_original_distance",
    "R": "race_was_resumed_to_complete_original_distance",
    "S": "race_was_restarted_or_resumed_without_completing_original_distance",
}


def build_full_url(url: str | None) -> str | None:
    if url is None:
        return None
    if isinstance(url, str) and url.startswith("/"):
        return WIKIPEDIA_BASE_URL + url
    return url


def try_int(text: str) -> int | str:
    try:
        return int(text)
    except ValueError:
        return text


def extract_rich_cell(
    cell_data: Any,
) -> tuple[str, list[Any], str | None, str | None]:
    if isinstance(cell_data, dict) and "text" in cell_data:
        text = cell_data.get("text") or ""
        links = cell_data.get("links") or []
        background = cell_data.get("background")
        url = build_full_url(links[0].get("url") if links else None)
        return text, links, background, url
    text = str(cell_data) if cell_data else ""
    return text, [], None, None


def map_winner_cell(text: str, links: list[Any]) -> dict[str, Any]:
    winner_link = links[-1] if links else None
    if winner_link:
        winner_text = strip_marks(winner_link.get("text") or "") or text
        return {"text": winner_text, "url": build_full_url(winner_link.get("url"))}
    return {"text": strip_marks(text) if text else text, "url": None}


def map_drivers_cell(text: str, links: list[Any]) -> list[dict[str, Any]]:
    if links:
        return [
            {
                "text": strip_marks(lnk.get("text") or ""),
                "url": build_full_url(lnk.get("url")),
            }
            for lnk in links
            if lnk.get("text")
        ]
    if text:
        return [{"text": strip_marks(text), "url": None}]
    return []
