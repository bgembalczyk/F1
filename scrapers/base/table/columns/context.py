from dataclasses import dataclass

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
    cell: Tag | None
    base_url: str
    skip_sentinel: object = SKIP_SENTINEL
    model_fields: set[str] | None = None
    header_link: LinkRecord | None = None
