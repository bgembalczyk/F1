from dataclasses import dataclass
from typing import Optional, Set

from bs4 import Tag

from models.records import LinkRecord


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
    links: list[LinkRecord]
    cell: Optional[Tag]
    skip_sentinel: object
    model_fields: Optional[Set[str]] = None
