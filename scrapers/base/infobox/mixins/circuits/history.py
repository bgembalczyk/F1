# scrapers/base/infobox/mixins/circuits/history.py

import re
from typing import Dict, Any, Optional, List

from scrapers.base.infobox.mixins.text_utils import InfoboxTextUtilsMixin


class CircuitHistoryMixin(InfoboxTextUtilsMixin):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground...)."""

    def _parse_former_names(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parsuje pole 'Former names' do listy dictów:

        [
          {"name": "Adelaide International Raceway", "years": "1982–1988"},
          {"name": "New Adelaide Circuit", "years": "1989–1995"},
          ...
        ]

        Jeżeli nie uda się wyciągnąć lat, 'years' będzie None.
        """
        if not row:
            return None

        items = self._split_simple_list(row) or []
        if not items:
            return None

        result: List[Dict[str, Any]] = []

        for item in items:
            s = (item or "").strip()
            if not s:
                continue

            # próbujemy wyciągnąć lata z nawiasów
            # np. "Adelaide International Raceway (1982–1988)"
            m = re.match(r"^(?P<name>.+?)\s*\((?P<years>[^)]+)\)\s*$", s)
            if m:
                name = m.group("name").strip()
                years = m.group("years").strip()
                if name:
                    result.append({"name": name, "years": years or None})
            else:
                # brak wzorca z nawiasami → mamy tylko nazwę
                result.append({"name": s, "years": None})

        return result or None

    def _parse_history(
        self, rows: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        def _dates_to_list(d: Dict[str, Any]) -> List[str]:
            if not d:
                return []
            # iso_dates preferowane, w przeciwnym razie surowe lata
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
            # Former names przeniesione tutaj i znormalizowane do listy dictów
            "former_names": self._parse_former_names(rows.get("Former names")),
            # UWAGA: owner usunięty – nie zwracamy go już w historii
        }

        return history
