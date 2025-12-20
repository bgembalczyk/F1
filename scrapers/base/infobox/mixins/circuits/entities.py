from __future__ import annotations

from typing import Optional, Dict, Any, List

from scrapers.base.infobox.mixins.circuits.geo import CircuitGeoMixin
from scrapers.base.infobox.mixins.circuits.history import CircuitHistoryMixin
from scrapers.base.infobox.mixins.circuits.specs import CircuitSpecsMixin
from scrapers.base.infobox.mixins.circuits.lap_record import CircuitLapRecordMixin


IGNORED_TOP_LEVEL_KEYS: set[str] = {
    # oryginalne labelki + wersje z małej litery na wszelki wypadek
    "Owner",
    "owner",
    "Operator",
    "operator",
    "Capacity",
    "capacity",
    "Construction cost",
    "construction cost",
    "Website",
    "website",
    "Area",
    "area",
    "Major events",
    "major events",
    "Address",
    "address",
}


class CircuitEntitiesMixin(CircuitLapRecordMixin, CircuitGeoMixin, CircuitSpecsMixin, CircuitHistoryMixin):
    """Łączy parsowanie linkowanych encji, lap recordów i buduje normalized/layouts."""


    # ------------------------------------
    # Normalized/layouts
    # ------------------------------------

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
            "Website",
            "Area",
            "Major events",
            "Address",
            "Architect",
            "Banking",
            "Surface",
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
            },
            "history": self._parse_history(rows),
            "architect": self._parse_linked_entity(rows.get("Architect")),
        }

        extra_fields = self._collect_additional_info(rows, used_keys)
        if extra_fields:
            normalized["additional_info"] = extra_fields

        normalized = self._prune_nulls(normalized)

        # --- RAW cleanup ---
        result: Dict[str, Any] = dict(raw or {})
        result.pop("rows", None)
        for key in IGNORED_TOP_LEVEL_KEYS:
            result.pop(key, None)

        # --- Layouts ---
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

        # jeśli są layouty, to dopilnuj że lap record z infoboxa nie zdubluje rekordów z layout_records
        if layouts:
            base_record = self._parse_lap_record(rows.get("Race lap record"))
            if base_record:
                matched = False

                # 1) spróbuj dopasować do istniejącego layoutu i zmergować
                for lay in layouts:
                    existing = lay.get("race_lap_record")
                    if not existing:
                        continue

                    if self._same_lap_record(base_record, existing):
                        lay["race_lap_record"] = self._merge_lap_record(existing, base_record)
                        matched = True
                        break

                # 2) jeśli nie ma dopasowania:
                if not matched:
                    # jeśli jest dokładnie jeden layout i nie ma rekordu – podepnij go tam
                    if len(layouts) == 1 and not layouts[0].get("race_lap_record"):
                        layouts[0]["race_lap_record"] = base_record
                    else:
                        # w innym wypadku dodaj dodatkowy "layout" tylko dla tego rekordu
                        layouts.append(
                            self._prune_nulls(
                                {
                                    "layout": None,
                                    "years": None,
                                    "race_lap_record": base_record,
                                }
                            )
                        )

            result["layouts"] = self._prune_nulls(layouts)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self._prune_nulls(result)
