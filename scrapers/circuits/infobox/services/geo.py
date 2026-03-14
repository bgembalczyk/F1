import re
from typing import TYPE_CHECKING
from typing import Any

from models.services.helpers import split_delimited_text
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.constants import LOCATION_STOPWORDS
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils

if TYPE_CHECKING:
    from models.records.link import LinkRecord

MIN_COORD_PARTS = 2


class CircuitGeoParser(InfoboxTextUtils):
    """Parsowanie lokalizacji, współrzędnych, powierzchni."""

    @staticmethod
    def _split_plain_segment(segment: str) -> list[str]:
        """Dzieli segment tekstu na części rozdzielone przecinkami, ukośnikami itp."""
        return [
            cleaned_part
            for part in split_delimited_text(segment, pattern=r"[,·/;]")
            if (cleaned_part := part.strip(" ,"))
            and cleaned_part.lower() not in LOCATION_STOPWORDS
        ]

    def _components_from_links(
        self,
        text: str,
        links: list["LinkRecord"],
    ) -> list[dict[str, Any]]:
        components: list[dict[str, Any]] = []
        cursor = 0

        for link in links:
            link_text = (link.get("text") or "").strip()
            if not link_text:
                continue

            idx = text.find(link_text, cursor)
            if idx == -1:
                continue

            before = text[cursor:idx]
            components.extend(
                {"text": part} for part in self._split_plain_segment(before)
            )
            components.append(
                {
                    "text": link_text,
                    "link": {
                        "text": link_text,
                        "url": link.get("url"),
                    },
                },
            )
            cursor = idx + len(link_text)

        tail = text[cursor:]
        components.extend({"text": part} for part in self._split_plain_segment(tail))
        return components

    @staticmethod
    def _filter_components(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            comp
            for comp in components
            if (txt := (comp.get("text") or "").strip())
            and txt.lower() not in LOCATION_STOPWORDS
        ]

    def parse_location(self, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if not row:
            return None

        text = clean_infobox_text(row.get("text")) or ""
        links: list[LinkRecord] = row.get("links") or []
        components = self._components_from_links(text, links)
        filtered_components = self._filter_components(components)

        if not filtered_components:
            return None

        return {
            f"localisation{idx}": comp
            for idx, comp in enumerate(filtered_components, start=1)
        }

    def parse_coordinates(
        self,
        row: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return self._parse_position(text)

    @staticmethod
    def _parse_position(text: str) -> dict[str, float] | None:
        if not text:
            return None
        try:
            decimal_match = re.search(r"(-?\d+(?:\.\d+)?);\s*(-?\d+(?:\.\d+)?)", text)
            if decimal_match:
                return {
                    "lat": float(decimal_match.group(1)),
                    "lon": float(decimal_match.group(2)),
                }

            parts = re.findall(r"([NSWE]?)(-?\d+(?:\.\d+)?)", text)
            if len(parts) >= MIN_COORD_PARTS:
                lat_dir, lat_val = parts[0]
                lon_dir, lon_val = parts[1]
                lat = float(lat_val)
                lon = float(lon_val)
                if lat_dir.upper() == "S":
                    lat = -lat
                if lon_dir.upper() == "W":
                    lon = -lon
                return {"lat": lat, "lon": lon}
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować współrzędnych: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

        return None

    @staticmethod
    def _parse_area(row: dict[str, Any] | None) -> dict[str, float] | None:
        """Area: np. '277 acres (112 ha)' -> acres + hectares."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        acres_match = re.search(r"([\d.,]+)\s*acres?", text, flags=re.IGNORECASE)
        ha_match = re.search(r"([\d.,]+)\s*ha\b", text, flags=re.IGNORECASE)

        def _to_float(s: str) -> float:
            return float(s.replace(",", "."))

        result: dict[str, float] = {}
        try:
            if acres_match:
                result["acres"] = _to_float(acres_match.group(1))
            if ha_match:
                result["hectares"] = _to_float(ha_match.group(1))
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować powierzchni: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

        return result or None
