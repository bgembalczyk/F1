import re
from datetime import datetime
from typing import Dict, Any, Optional, List

from scrapers.base.infobox.circuits.services.constants import _MONTHS
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitHistoryParser(InfoboxTextUtils):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground, Former names...)."""

    def _parse_former_names(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parsuje 'Former names' do listy dictów.
        """

        if not row:
            return None

        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        results: List[Dict[str, Any]] = []

        pattern = re.compile(
            r"(?P<name>.+?)\s*\((?P<periods>[^)]*?\d[^)]*?)\)",
            flags=re.UNICODE,
        )

        matches = list(pattern.finditer(text))

        if not matches:
            cleaned = text.strip()
            if not cleaned:
                return None
            results.append({"name": cleaned, "periods": []})
            return results

        for m in matches:
            name_raw = (m.group("name") or "").strip(" ;,/")
            periods_raw = (m.group("periods") or "").strip()

            if not name_raw:
                continue

            periods = self._parse_periods_string(periods_raw)
            results.append(
                {
                    "name": name_raw,
                    "periods": periods,
                }
            )

        return results or None

    def _parse_periods_string(self, periods_raw: str) -> List[Dict[str, str]]:
        """
        Normalizuje zakresy lat do listy dictów.
        """
        now_year = datetime.now().year
        periods: List[Dict[str, str]] = []

        segments = [seg.strip() for seg in periods_raw.split(",") if seg.strip()]
        if not segments:
            return periods

        for seg in segments:
            if "–" in seg:
                start_raw, end_raw = seg.split("–", 1)
            elif "-" in seg:
                start_raw, end_raw = seg.split("-", 1)
            else:
                start_raw, end_raw = seg, ""

            start = self._normalize_period_endpoint(
                start_raw, is_start=True, now_year=now_year
            )
            end = self._normalize_period_endpoint(
                end_raw, is_start=False, now_year=now_year
            )

            if start is None and end is None:
                continue

            period: Dict[str, str] = {}
            if start is not None:
                period["from"] = start
            if end is not None:
                period["to"] = end

            if period:
                periods.append(period)

        return periods

    @staticmethod
    def _normalize_period_endpoint(
        raw: str, *, is_start: bool, now_year: int
    ) -> Optional[str]:
        """
        Normalizuje pojedynczy kraniec zakresu (from/to) do stringa.
        """
        s = (raw or "").strip()
        if not s:
            return None

        lower = s.lower()

        if not is_start and lower in {"present", "present day", "current", "now"}:
            return str(now_year)

        m = re.search(
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})",
            lower,
        )
        if m:
            month_name = m.group(1)
            year = int(m.group(2))
            month = _MONTHS[month_name]
            return f"{year:04d}-{month:02d}"

        m = re.search(r"(\d{4})s\b", lower)
        if m:
            year = int(m.group(1))
            if is_start:
                return str(year)
            return str(year + 9)

        m = re.search(r"(\d{4})", lower)
        if m:
            year = int(m.group(1))
            return str(year)

        return None

    def parse_history(
        self, rows: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        def _dates_to_list(d: Dict[str, Any]) -> List[str]:
            if not d:
                return []
            return d.get("iso_dates") or d.get("years") or []

        opened_dates = self._parse_dates(rows.get("Opened")) or {}
        for idx, date in enumerate(_dates_to_list(opened_dates)):
            events.append(
                {
                    "event": "opened" if idx == 0 else "reopened",
                    "date": date,
                }
            )

        closed_dates = self._parse_dates(rows.get("Closed")) or {}
        for date in _dates_to_list(closed_dates):
            events.append({"event": "closed", "date": date})

        broke_ground_dates = self._parse_dates(rows.get("Broke ground")) or {}
        for date in _dates_to_list(broke_ground_dates):
            events.append({"event": "broke_ground", "date": date})

        built_dates = self._parse_dates(rows.get("Built")) or {}
        for date in _dates_to_list(built_dates):
            events.append({"event": "built", "date": date})

        events = sorted(events, key=lambda e: e.get("date") or "")

        history: Dict[str, Any] = {
            "events": events or None,
            "former_names": self._parse_former_names(rows.get("Former names")),
        }

        return history
