from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from bs4 import Tag

from scrapers.helpers.f1_table_utils import clean_wiki_text


@dataclass
class ColumnContext:
    """
    Kontekst pojedynczej komórki tabeli.

    Kolumny operują głównie na:
    - raw_text,
    - clean_text,
    - links (lista {text, url}),
    ale nadal mają dostęp do cell, jeśli bardzo potrzebują.
    """

    header: str
    key: str
    raw_text: str
    clean_text: str
    links: list[dict[str, Any]]
    cell: Tag
    skip_sentinel: object
