from typing import Optional, Dict, Any, List

from scrapers.base.infobox.circuits.services.constants import (
    IGNORED_TOP_LEVEL_KEYS,
    used_keys,
)
from scrapers.circuits.infobox.services.additional_info import CircuitAdditionalInfoParser
from scrapers.circuits.infobox.services.entity_parsing import CircuitEntityParser
from scrapers.circuits.infobox.services.geo import CircuitGeoParser
from scrapers.circuits.infobox.services.history import CircuitHistoryParser
from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils

class CircuitEntitiesParser:
    """Łączy parsowanie linkowanych encji, lap recordów i buduje normalized/layouts."""

    def __init__(
        self,
        *,
        text_utils: InfoboxTextUtils,
        geo_parser: CircuitGeoParser,
        history_parser: CircuitHistoryParser,
        specs_parser: CircuitSpecsParser,
        lap_record_parser: CircuitLapRecordParser,
        entity_parser: CircuitEntityParser,
        additional_info_parser: CircuitAdditionalInfoParser,
    ) -> None:
        self.text_utils = text_utils
        self.geo_parser = geo_parser
        self.history_parser = history_parser
        self.specs_parser = specs_parser
        self.lap_record_parser = lap_record_parser
        self.entity_parser = entity_parser
        self.additional_info_parser = additional_info_parser

    def with_normalized(
        self,
        raw: Dict[str, Any],
        layout_records: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        rows: Dict[str, Dict[str, Any]] = raw.get("rows", {}) if raw else {}

        normalized: Dict[str, Any] = {
            "name": raw.get("title"),
            "location": self.geo_parser.parse_location(rows.get("Location")),
            "coordinates": self.geo_parser.parse_coordinates(rows.get("Coordinates")),
            "specs": {
                "fia_grade": self.text_utils.parse_int(rows.get("FIA Grade")),
                "length_km": self.text_utils.parse_length(
                    rows.get("Length"), unit="km"
                ),
                "length_mi": self.text_utils.parse_length(
                    rows.get("Length"), unit="mi"
                ),
                "turns": self.text_utils.parse_int(rows.get("Turns")),
            },
            "history": self.history_parser.parse_history(rows),
            "architect": self.entity_parser.parse_linked_entity(rows.get("Architect")),
        }

        extra_fields = self.additional_info_parser.collect_additional_info(
            rows, used_keys
        )
        if extra_fields:
            normalized["additional_info"] = extra_fields

        normalized = self.text_utils.prune_nulls(normalized)

        result: Dict[str, Any] = dict(raw or {})
        result.pop("rows", None)
        for key in IGNORED_TOP_LEVEL_KEYS:
            result.pop(key, None)

        layouts = layout_records or []

        if not layouts:
            default_layout: Dict[str, Any] = {
                "layout": None,
                "years": None,
                "length_km": normalized.get("specs", {}).get("length_km"),
                "length_mi": normalized.get("specs", {}).get("length_mi"),
                "turns": normalized.get("specs", {}).get("turns"),
                "race_lap_record": self.lap_record_parser.parse_lap_record(
                    rows.get("Race lap record")
                ),
                "surface": self.specs_parser.parse_surface(rows.get("Surface")),
                "banking": self.specs_parser.parse_banking(rows.get("Banking")),
            }
            default_layout = self.text_utils.prune_nulls(default_layout)
            if default_layout:
                layouts = [default_layout]

        if layouts:
            base_record = self.lap_record_parser.parse_lap_record(
                rows.get("Race lap record")
            )
            if base_record:
                matched = False

                for lay in layouts:
                    existing = lay.get("race_lap_record")
                    if not existing:
                        continue

                    if self.lap_record_parser.same_lap_record(base_record, existing):
                        lay["race_lap_record"] = (
                            self.lap_record_parser.merge_lap_record(
                                existing, base_record
                            )
                        )
                        matched = True
                        break

                if not matched:
                    if len(layouts) == 1 and not layouts[0].get("race_lap_record"):
                        layouts[0]["race_lap_record"] = base_record
                    else:
                        layouts.append(
                            self.text_utils.prune_nulls(
                                {
                                    "layout": None,
                                    "years": None,
                                    "race_lap_record": base_record,
                                }
                            )
                        )

            result["layouts"] = self.text_utils.prune_nulls(layouts)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self.text_utils.prune_nulls(result)
