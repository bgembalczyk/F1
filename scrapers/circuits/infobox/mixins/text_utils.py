import re
from typing import Optional, Dict, Any, List


class InfoboxTextUtilsMixin:
    """Ogólne helpery do pracy na dictach z infoboksa."""

    def _get_text(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = row.get("text")
        if not isinstance(text, str):
            return None

        text = re.sub(r"\[\s*\d+\s*]", "", text)  # przypisy [ 2 ], [3]
        text = re.sub(r"\s+", " ", text)
        return text.strip() or None

    def _split_simple_list(self, row: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
        return parts or None

    def _parse_int(self, row: Optional[Dict[str, Any]]) -> Optional[int]:
        if not row:
            return None
        text = self._get_text(row) or ""
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _parse_length(
        self, row: Optional[Dict[str, Any]], *, unit: str
    ) -> Optional[float]:
        if not row:
            return None
        text = self._get_text(row) or ""
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*" + re.escape(unit), text)
        return float(match.group(1)) if match else None

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

    def _find_link(
        self,
        text: Optional[str],
        links: List[Dict[str, str]],
    ) -> Optional[Dict[str, str]]:
        if not text:
            return None
        for link in links:
            if link.get("text", "").strip().lower() == text.strip().lower():
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
        return {"text": text, "url": link.get("url") if link else None}

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
