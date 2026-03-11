from dataclasses import dataclass
from typing import Optional
from typing import Set

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.table.constants import SKIP_SENTINEL


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
    raw_text: str | None
    clean_text: str | None
    links: list[LinkRecord]
    cell: Optional[Tag]
    base_url: str
    skip_sentinel: object = SKIP_SENTINEL
    model_fields: Optional[Set[str]] = None
    header_link: LinkRecord | None = None
