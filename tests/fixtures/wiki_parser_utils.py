from __future__ import annotations

from bs4 import BeautifulSoup
from bs4 import Tag


def make_soup(html: str) -> BeautifulSoup:
    """Build BeautifulSoup with the parser used across wiki parser tests."""

    return BeautifulSoup(html, "html.parser")


def as_root_children(soup: BeautifulSoup, *, root: str = "div") -> list:
    """Return direct Tag children of the first root element."""

    container = soup.find(root)
    if container is None:
        return []
    return [child for child in container.children if isinstance(child, Tag)]
