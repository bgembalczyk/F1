import re
from typing import Optional, Dict, Any, List

from scrapers.base.helpers.text import split_delimited_text, parse_int_from_text, parse_number_with_unit
from scrapers.base.helpers.wiki import is_wikipedia_redlink


class InfoboxTextUtils:
    """Ogólne helpery do pracy na dictach z infoboksa."""

    # ------------------------------
    # Tekst
    # ------------------------------

    def _get_text(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = row.get("text")
        if not isinstance(text, str):
            return None

        # usuwamy przypisy [ 2 ], [3] oraz markery językowe [ it ], [ fr ] itp.
        # (typowy pattern w infoboksach: "Jarno Zaffelli [ it ]")
        text = re.sub(r"\[\s*(?:\d+|[a-z]{1,3})\s*]", "", text)

        # normalizacja whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip() or None

    # ------------------------------
    # Proste listy / liczby / długości
    # ------------------------------

    def _split_simple_list(self, row: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = split_delimited_text(text)
        return parts or None

    def _parse_int(self, row: Optional[Dict[str, Any]]) -> Optional[int]:
        if not row:
            return None
        text = self._get_text(row) or ""
        return parse_int_from_text(text)

    def _parse_length(
        self, row: Optional[Dict[str, Any]], *, unit: str
    ) -> Optional[float]:
        if not row:
            return None
        text = self._get_text(row) or ""
        return parse_number_with_unit(text, unit=unit)

    def _parse_dates(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parsyje daty typu YYYY-MM-DD, YYYY-MM, YYYY i zwraca też listę lat."""
        if not row:
            return None
        text = self._get_text(row) or ""
        if not text:
            return None

        iso_full = re.findall(r"\d{4}-\d{2}-\d{2}", text)
        iso_month = re.findall(r"\d{4}-\d{2}", text)
        years = re.findall(r"\b(1[89]\d{2}|20\d{2})\b", text)

        iso_dates: List[str] = []
        if iso_full:
            iso_dates = iso_full
        elif iso_month:
            iso_dates = iso_month

        return {
            "text": text or None,
            "iso_dates": iso_dates or None,
            "years": years or None,
        }

    # ------------------------------
    # Linki
    # ------------------------------

    def _find_link(
        self,
        text: Optional[str],
        links: List[Dict[str, str]],
    ) -> Optional[Dict[str, str]]:
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
        links: Optional[List[Dict[str, str]]],
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

    def _prune_nulls(self, data: Any) -> Any:
        if isinstance(data, dict):
            pruned_dict = {}
            for key, value in data.items():
                cleaned = self._prune_nulls(value)
                if cleaned is None:
                    continue
                if isinstance(cleaned, (dict, list)) and len(cleaned) == 0:
                    continue
                pruned_dict[key] = cleaned
            return pruned_dict

        if isinstance(data, list):
            pruned_list = []
            for value in data:
                cleaned = self._prune_nulls(value)
                if cleaned is None:
                    continue
                if isinstance(cleaned, (dict, list)) and len(cleaned) == 0:
                    continue
                pruned_list.append(cleaned)
            return pruned_list

        return data
