from __future__ import annotations

import re
from typing import Optional, Dict, Any, List

from scrapers.circuits.infobox.mixins.geo import CircuitGeoMixin
from scrapers.circuits.infobox.mixins.history import CircuitHistoryMixin
from scrapers.circuits.infobox.mixins.specs import CircuitSpecsMixin
from scrapers.circuits.infobox.mixins.text_utils import InfoboxTextUtilsMixin


class CircuitEntitiesMixin(
    InfoboxTextUtilsMixin,
    CircuitGeoMixin,
    CircuitSpecsMixin,
    CircuitHistoryMixin,
):
    """Łączy parsowanie linkowanych encji, lap recordów i buduje normalized/layouts."""

    def _parse_linked_entity(
        self,
        row: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any] | str | List[Dict[str, Any]]]:
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        links = row.get("links") or []

        if len(links) > 1:
            entities: List[Dict[str, Any]] = []
            for link in links:
                link_text = (link.get("text") or "").strip()
                if not link_text:
                    continue
                entities.append(
                    {
                        "text": link_text,
                        "url": link.get("url"),
                    },
                )
            return entities or None

        parts = [p.strip() for p in re.split(r"\s*(?:,|&| and )\s*", text) if p.strip()]

        def _entity_for_part(part: str) -> Dict[str, Any]:
            link = self._find_link(part, links)
            if link and link.get("url"):
                return {"text": part, "url": link.get("url")}
            return {"text": part}

        if len(parts) > 1:
            return [_entity_for_part(p) for p in parts]

        if links:
            url = links[0].get("url")
            if url:
                return {"text": text, "url": url}
        return text or None

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = self._get_text(row) or ""
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None

    def _collect_additional_info(
        self, rows: Dict[str, Dict[str, Any]], used_keys: set[str]
    ) -> Optional[Dict[str, Any]]:
        additional: Dict[str, Any] = {}

        for key, row in rows.items():
            if key in used_keys:
                continue

            text = self._get_text(row)
            if not text:
                continue

            info: Dict[str, Any] = {"text": text}
            links = row.get("links") or []

            parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
            if len(parts) > 1:
                values: List[Any] = []
                for part in parts:
                    link = self._find_link(part, links)
                    if link:
                        values.append({"text": part, "url": link.get("url")})
                    else:
                        values.append(part)
                info["values"] = values
            elif links:
                info["links"] = links

            additional[key] = info

        return additional or None

    def _parse_lap_record(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        text = self._get_text(row) or ""
        time_match = re.search(r"\d+:\d{2}\.\d{3}", text)
        details_match = re.search(r"\(([^)]*)\)", text)

        details: List[str] = []
        if details_match:
            details = [
                part.strip()
                for part in details_match.group(1).split(",")
                if part.strip()
            ]

        record: Dict[str, Any] = {
            "time": time_match.group(0) if time_match else None,
        }

        if details:
            driver_text = details[0] if len(details) >= 1 else None
            car_text = details[1] if len(details) >= 2 else None
            record.update(
                {
                    "driver": self._with_link(driver_text, row.get("links")),
                    "car": self._with_link(car_text, row.get("links")),
                    "year": details[2] if len(details) >= 3 else None,
                    "series": details[3] if len(details) >= 4 else None,
                }
            )

        return record

    def _same_lap_record(
        self, left: Optional[Dict[str, Any]], right: Optional[Dict[str, Any]]
    ) -> bool:
        if not left or not right:
            return False

        def _text(obj: Optional[Dict[str, Any]]) -> Optional[str]:
            if not obj:
                return None
            return obj.get("text") if isinstance(obj, dict) else None

        return (
            left.get("time") == right.get("time")
            and _text(left.get("driver")) == _text(right.get("driver"))
            and _text(left.get("car")) == _text(right.get("car"))
            and left.get("year") == right.get("year")
            and left.get("series") == right.get("series")
        )

    def _lap_record_exists(
        self, candidate: Dict[str, Any], records: List[Dict[str, Any]]
    ) -> bool:
        for record in records:
            if self._same_lap_record(candidate, record.get("race_lap_record")):
                return True
        return False

    def _merge_records(
        self, base_record_row: Optional[Dict[str, Any]], layouts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        for layout in layouts:
            if layout.get("race_lap_record"):
                records.append(self._prune_nulls(layout))

        base_record = self._parse_lap_record(base_record_row)
        if base_record and not self._lap_record_exists(base_record, records):
            records.append({"race_lap_record": base_record})

        return records

    def _with_normalized(
        self,
        raw: Dict[str, Any],
        layout_records: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        rows: Dict[str, Dict[str, Any]] = raw.get("rows", {}) if raw else {}

        used_keys = {
            "Location",
            "Coordinates",
            "FIA Grade",
            "Length",
            "Turns",
            "Race lap record",
            "Opened",
            "Closed",
            "Former names",
            "Owner",
            "Operator",
            "Capacity",
            "Broke ground",
            "Built",
            "Construction cost",
            "Architect",
            "Website",
            "Banking",
            "Surface",
            "Area",
        }

        normalized: Dict[str, Any] = {
            "name": raw.get("title"),
            "location": self._parse_location(rows.get("Location")),
            "coordinates": self._parse_coordinates(rows.get("Coordinates")),
            "specs": {
                "fia_grade": self._parse_int(rows.get("FIA Grade")),
                "length_km": self._parse_length(rows.get("Length"), unit="km"),
                "length_mi": self._parse_length(rows.get("Length"), unit="mi"),
                "turns": self._parse_int(rows.get("Turns")),
                "capacity": self._parse_capacity(rows.get("Capacity")),
                "construction_cost": self._parse_construction_cost(
                    rows.get("Construction cost"),
                ),
                "area": self._parse_area(rows.get("Area")),
            },
            "history": self._parse_history(rows),
            "operator": self._parse_linked_entity(rows.get("Operator")),
            "architect": self._parse_linked_entity(rows.get("Architect")),
            "website": self._parse_website(rows.get("Website")),
        }

        extra_fields = self._collect_additional_info(rows, used_keys)
        if extra_fields:
            normalized["additional_info"] = extra_fields

        normalized = self._prune_nulls(normalized)

        result: Dict[str, Any] = dict(raw or {})
        result.pop("rows", None)

        layouts = layout_records or []
        if not layouts:
            default_layout: Dict[str, Any] = {
                "layout": None,
                "years": None,
                "length_km": normalized.get("specs", {}).get("length_km"),
                "length_mi": normalized.get("specs", {}).get("length_mi"),
                "turns": normalized.get("specs", {}).get("turns"),
                "race_lap_record": self._parse_lap_record(rows.get("Race lap record")),
                "surface": self._parse_surface(rows.get("Surface")),
                "banking": self._parse_banking(rows.get("Banking")),
            }
            default_layout = self._prune_nulls(default_layout)
            if default_layout:
                layouts = [default_layout]

        if layouts:
            result["layouts"] = self._prune_nulls(layouts)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self._prune_nulls(result)
