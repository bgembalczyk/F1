from typing import TYPE_CHECKING
from typing import Any

from scrapers.helpers.text_normalization import clean_infobox_text
from scrapers.helpers.text_normalization import split_delimited_text
from scrapers.parsers.infobox.text_utils.circuit.text_processing.entity.base import (
    CircuitEntityExtractor,
)

if TYPE_CHECKING:
    from models.records.link import LinkRecord


class CircuitAdditionalInfoExtractor(CircuitEntityExtractor):
    """Zbieranie dodatkowych pól (additional_info)."""

    def parse(
        self,
        rows: dict[str, dict[str, Any]],
        used_keys: set[str],
    ) -> dict[str, Any] | None:
        return self.collect_additional_info(rows, used_keys)

    def collect_additional_info(
        self,
        rows: dict[str, dict[str, Any]],
        used_keys: set[str],
    ) -> dict[str, Any] | None:
        additional: dict[str, Any] = {}

        for key, row in rows.items():
            if key in used_keys:
                continue

            text = (clean_infobox_text(row.get("text")) or "").strip()
            if not text:
                continue

            info: dict[str, Any] = {"text": text}
            links: list[LinkRecord] = row.get("links") or []

            parts = split_delimited_text(text)
            if len(parts) > 1:
                values: list[Any] = []
                for part in parts:
                    link = self._find_link(part, links)
                    if link and link.get("url"):
                        values.append({"text": part, "url": link.get("url")})
                    else:
                        values.append(part)
                info["values"] = values
            elif links:
                # tutaj nie czyścimy agresywnie - to tylko additional_info
                info["links"] = links

            additional[key] = info

        return additional or None


__all__ = ["CircuitAdditionalInfoExtractor"]
