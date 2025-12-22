from typing import Any, Dict, List, Optional

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import split_delimited_text
from scrapers.circuits.infobox.services.entity_parsing import CircuitEntityParser


class CircuitAdditionalInfoParser(CircuitEntityParser):
    """Zbieranie dodatkowych pól (additional_info)."""

    def collect_additional_info(
        self, rows: Dict[str, Dict[str, Any]], used_keys: set[str]
    ) -> Optional[Dict[str, Any]]:
        additional: Dict[str, Any] = {}

        for key, row in rows.items():
            if key in used_keys:
                continue

            text = (self._get_text(row) or "").strip()
            if not text:
                continue

            info: Dict[str, Any] = {"text": text}
            links: List[LinkRecord] = row.get("links") or []

            parts = split_delimited_text(text)
            if len(parts) > 1:
                values: List[Any] = []
                for part in parts:
                    link = self._find_link(part, links)
                    if link and link.get("url"):
                        values.append({"text": part, "url": link.get("url")})
                    else:
                        values.append(part)
                info["values"] = values
            elif links:
                # tutaj nie czyścimy agresywnie – to tylko additional_info
                info["links"] = links

            additional[key] = info

        return additional or None
