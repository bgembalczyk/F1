from typing import Optional, Dict, Any, List

from models.records.link import LinkRecord
from scrapers.base.helpers.parsing import parse_int_from_text, parse_number_with_unit
from scrapers.base.helpers.prune import prune_empty
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.text_normalization import (
    clean_infobox_text,
    split_delimited_text,
)
from scrapers.base.helpers.wiki import is_wikipedia_redlink


class InfoboxTextUtils:
    """Ogólne helpery do pracy na dictach z infoboksa."""

    # ------------------------------
    # Tekst
    # ------------------------------

    # ------------------------------
    # Proste listy / liczby / długości
    # ------------------------------

    def _split_simple_list(self, row: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        parts = split_delimited_text(text)
        return parts or None

    def parse_int(self, row: Optional[Dict[str, Any]]) -> Optional[int]:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return parse_int_from_text(text)

    def parse_length(
        self, row: Optional[Dict[str, Any]], *, unit: str
    ) -> Optional[float]:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return parse_number_with_unit(text, unit=unit)

    def _parse_dates(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parsyje daty typu YYYY-MM-DD, YYYY-MM, YYYY i zwraca też listę lat."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None
        parsed = parse_date_text(text)
        iso = parsed.get("iso")
        if isinstance(iso, list):
            iso_dates = iso or None
        elif isinstance(iso, str):
            iso_dates = [iso]
        else:
            iso_dates = None

        return {
            "text": parsed.get("text"),
            "iso_dates": iso_dates,
            "years": parsed.get("years"),
        }

    # ------------------------------
    # Linki
    # ------------------------------

    @staticmethod
    def _find_link(
        text: Optional[str],
        links: List[LinkRecord],
    ) -> Optional[LinkRecord]:
        if not text:
            return None
        wanted = text.strip().lower()
        for link in links:
            link_text = link.get("text", "")
            if link_text and link_text.strip().lower() == wanted:
                return link
        return None

    def _with_link(
        self,
        text: Optional[str],
        links: Optional[List[LinkRecord]],
    ) -> Optional[Dict[str, Any]]:
        if text is None:
            return None
        link = self._find_link(text, links or [])

        url: Optional[str] = None
        if link:
            candidate = link.get("url")
            # ignorujemy redlinki Wikipedii
            if candidate and not is_wikipedia_redlink(candidate):
                url = candidate

        return {"text": text, "url": url}

    # ------------------------------
    # Czyszczenie None / pustych struktur
    # ------------------------------

    def prune_nulls(self, data: Any) -> Any:
        return prune_empty(
            data,
            drop_empty_lists=True,
            drop_none=True,
            drop_empty_dicts=True,
        )
