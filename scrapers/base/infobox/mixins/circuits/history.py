# scrapers/base/infobox/mixins/circuits/history.py

import re
from datetime import datetime
from typing import Dict, Any, Optional, List

from scrapers.base.infobox.mixins.text_utils import InfoboxTextUtilsMixin


_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


class CircuitHistoryMixin(InfoboxTextUtilsMixin):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground, Former names...)."""

    # -------------------------
    # Former names
    # -------------------------

    def _parse_former_names(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parsuje 'Former names' do listy dictów:

        [
          {
            "name": "Autódromo Magdalena Mixhuca",
            "periods": [
              {"from": "1959", "to": "1979"},
              ...
            ]
          },
          ...
        ]

        Obsługiwane przypadki:
        - "Name (1959–1979)"
        - "Name (1960s–1989)"
        - "Name (1955–1960s)"
        - "Name (August 2005–September 2012, April 2024–May 2025)"
        - "Name (1984–present)"
        """

        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        results: List[Dict[str, Any]] = []

        # Wzorzec: NAME (COŚ_Z_LATAMI)
        # przykład: "İstanbul Park (August 2005–September 2012, April 2024–May 2025)"
        pattern = re.compile(
            r"(?P<name>.+?)\s*\((?P<periods>[^)]*?\d[^)]*?)\)",
            flags=re.UNICODE,
        )

        matches = list(pattern.finditer(text))

        if not matches:
            # fallback: próbujmy potraktować cały tekst jako jedną nazwę bez okresów
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
        Zamienia string typu:
            "1959–1979"
            "1960s–1989"
            "1955–1960s"
            "August 2005–September 2012, April 2024–May 2025"
            "October 2012–March 2024"
            "1984–present"

        na listę:
            [
              {"from": "1959", "to": "1979"},
              {"from": "2005-08", "to": "2012-09"},
              {"from": "2024-04", "to": "2025-05"},
              ...
            ]
        """
        now_year = datetime.now().year
        periods: List[Dict[str, str]] = []

        # kilka okresów rozdzielonych przecinkami
        segments = [seg.strip() for seg in periods_raw.split(",") if seg.strip()]
        if not segments:
            return periods

        for seg in segments:
            # segment typu "1959–1979" albo "August 2005–September 2012"
            if "–" in seg:
                start_raw, end_raw = seg.split("–", 1)
            elif "-" in seg:
                start_raw, end_raw = seg.split("-", 1)
            else:
                # pojedyncza wartość, np. samo "1960s" – ignorujemy "to" i ustawiamy tylko "from"
                start_raw, end_raw = seg, ""

            start = self._normalize_period_endpoint(start_raw, is_start=True, now_year=now_year)
            end = self._normalize_period_endpoint(end_raw, is_start=False, now_year=now_year)

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

    def _normalize_period_endpoint(
        self, raw: str, *, is_start: bool, now_year: int
    ) -> Optional[str]:
        """
        Normalizuje pojedynczy kraniec zakresu (from/to) do stringa.

        Obsługiwane formy:
        - "1959"
        - "1960s"      -> from: "1960", to: "1969"
        - "August 2005" -> "2005-08"
        - "present" / "present day" / "current" (tylko dla końca zakresu) -> str(now_year)
        """
        s = (raw or "").strip()
        if not s:
            return None

        lower = s.lower()

        # present / current tylko jako "to"
        if not is_start and lower in {"present", "present day", "current", "now"}:
            return str(now_year)

        # MIESIĄC + ROK, np. "August 2005"
        m = re.search(
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})",
            lower,
        )
        if m:
            month_name = m.group(1)
            year = int(m.group(2))
            month = _MONTHS[month_name]
            return f"{year:04d}-{month:02d}"

        # DEKADA, np. "1960s"
        m = re.search(r"(\d{4})s\b", lower)
        if m:
            year = int(m.group(1))
            if is_start:
                # początek dekady: 1960s -> 1960
                return str(year)
            else:
                # koniec dekady: 1960s -> 1969
                return str(year + 9)

        # ZWYKŁY ROK
        m = re.search(r"(\d{4})", lower)
        if m:
            year = int(m.group(1))
            return str(year)

        return None

    # -------------------------
    # Reszta historii
    # -------------------------

    def _parse_history(
        self, rows: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        def _dates_to_list(d: Dict[str, Any]) -> List[str]:
            if not d:
                return []
            return d.get("iso_dates") or d.get("years") or []  # type: ignore[return-value]

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
            # UWAGA: owner już usunięty
        }

        return history
