"""Shared helpers for building link lookup dictionaries."""

from models.records.link import LinkRecord


def build_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
    """Map normalized link text to matching link records."""
    lookup: dict[str, list[LinkRecord]] = {}
    for link in links:
        text = link.get("text")
        if not text:
            continue
        key = text.strip().lower()
        if key not in lookup:
            lookup[key] = []
        lookup[key].append(link)
    return lookup
