from typing import Dict, Any, Optional, List
import re

from scrapers.base.infobox.mixins.text_utils import InfoboxTextUtilsMixin


class CircuitHistoryMixin(InfoboxTextUtilsMixin):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground, Former names...)."""

    def _parse_former_names(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parsuje 'Former names' do listy dictów:

        [
          {"name": "Autodromo Dino Ferrari", "years": "1957–1988"},
          {"name": "Autodromo di Imola", "years": "1953–1956"},
          ...
        ]

        Szukamy wielokrotnych sekwencji:
            <NAME> (<YEARS>)
        w jednym stringu.
        """
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        result: List[Dict[str, Any]] = []

        # NAME (YEARS) NAME2 (YEARS2) ...
        # NAME – minimalnie zachłanny, YEARS – zawartość nawiasu
        pattern = re.compile(
            r"(?P<name>.+?)\s*\((?P<years>[^)]*?\d{3,4}[^)]*?)\)\s*"
        )

        for m in pattern.finditer(text):
            name = (m.group("name") or "").strip(" ,;/")
            years = (m.group("years") or "").strip()
            if name:
                result.append(
                    {
                        "name": name,
                        "years": years or None,
                    }
                )

        if result:
            return result

        # fallback – nic nie dopasowało wzorca NAME (YEARS)
        text = text.strip()
        if not text:
            return None
        return [{"name": text, "years": None}]

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
            # owner usunięty – nie pojawia się w historii
        }

        return history
