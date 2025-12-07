from typing import Dict, Any, Optional, List

from scrapers.base.infobox.mixins.text_utils import InfoboxTextUtilsMixin


class CircuitHistoryMixin(InfoboxTextUtilsMixin):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground...)."""

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

        history = {
            "events": events or None,
            "former_names": self._split_simple_list(rows.get("Former names")),
            "owner": self._get_text(rows.get("Owner")),
        }

        return history
