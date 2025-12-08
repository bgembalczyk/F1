from __future__ import annotations

from pathlib import Path

from scrapers.base.scraper import F1Scraper


def build_output_path(scraper: F1Scraper, base_dir: str | Path, *, extension: str) -> Path:
    """Zbuduj ścieżkę do pliku na podstawie atrybutów scrapera.

    Wymaga zdefiniowania ``data_resource`` (podkatalog w ``data/wiki`` lub innym
    katalogu bazowym) oraz ``data_file_stem`` (nazwa pliku bez rozszerzenia).
    """

    resource = getattr(scraper, "data_resource", None)
    file_stem = getattr(scraper, "data_file_stem", None)

    if not resource or not file_stem:
        raise ValueError("Scraper musi definiować 'data_resource' i 'data_file_stem'.")

    return Path(base_dir) / resource / f"{file_stem}.{extension}"
