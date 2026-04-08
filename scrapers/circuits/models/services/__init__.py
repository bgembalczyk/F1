from scrapers.circuits.models.services.circuit_service import CircuitService
from scrapers.circuits.models.services.constants import LAYOUT_LENGTH_TOLERANCE_KM
from scrapers.circuits.models.services.constants import TOP_LEVEL_KEYS
from scrapers.circuits.models.services.lap_record_merging import (
    are_subset_values_compatible,
)
from scrapers.circuits.models.services.lap_record_merging import build_core_key
from scrapers.circuits.models.services.lap_record_merging import collect_other_fields
from scrapers.circuits.models.services.lap_record_merging import (
    fill_missing_fields_from_extra,
)
from scrapers.circuits.models.services.lap_record_merging import first_present_value
from scrapers.circuits.models.services.lap_record_merging import (
    is_empty_or_missing_value,
)
from scrapers.circuits.models.services.lap_record_merging import is_record_subset
from scrapers.circuits.models.services.lap_record_merging import merge_best_entity
from scrapers.circuits.models.services.lap_record_merging import merge_date_or_year
from scrapers.circuits.models.services.lap_record_merging import merge_race_lap_records
from scrapers.circuits.models.services.lap_record_merging import merge_record_group
from scrapers.circuits.models.services.lap_record_merging import merge_series
from scrapers.circuits.models.services.lap_record_merging import merge_time
from scrapers.circuits.models.services.lap_record_merging import merge_two_records
from scrapers.circuits.models.services.lap_record_merging import normalize_entity_value
from scrapers.circuits.models.services.lap_record_merging import normalize_lap_record
from scrapers.circuits.models.services.lap_record_merging import same_dict_text_value
from scrapers.circuits.models.services.lap_record_merging import same_time_value
from scrapers.circuits.models.services.lap_record_merging import select_best_date_year
from scrapers.circuits.models.services.lap_record_merging import select_best_series
from scrapers.circuits.models.services.lap_record_merging import series_candidate
from scrapers.circuits.models.services.lap_record_merging import (
    stage_a_partition_by_record_key,
)
from scrapers.circuits.models.services.lap_record_merging import (
    stage_b_merge_by_core_key,
)
from scrapers.circuits.models.services.lap_record_merging import (
    stage_c_merge_by_driver_time,
)
from scrapers.circuits.models.services.lap_record_merging import (
    stage_d_fallback_merge_by_time_and_driver,
)
from scrapers.circuits.models.services.lap_record_utils import build_lap_record_key
from scrapers.circuits.models.services.lap_record_utils import extract_year
from scrapers.circuits.models.services.lap_record_utils import extract_year_from_event
from scrapers.circuits.models.services.lap_record_utils import has_meaningful_value
from scrapers.circuits.models.services.lap_record_utils import (
    normalize_lap_record_entity,
)
from scrapers.circuits.models.services.lap_record_utils import (
    parse_lap_record_time_from_record,
)
from scrapers.circuits.models.services.lap_record_utils import (
    select_best_field_with_url,
)
from scrapers.circuits.models.services.normalization import add_place
from scrapers.circuits.models.services.normalization import add_places_from_loc_norm
from scrapers.circuits.models.services.normalization import add_places_from_raw_dict
from scrapers.circuits.models.services.normalization import add_places_from_raw_list
from scrapers.circuits.models.services.normalization import add_places_from_raw_location
from scrapers.circuits.models.services.normalization import extract_circuit_location
from scrapers.circuits.models.services.normalization import extract_circuit_names
from scrapers.circuits.models.services.normalization import extract_circuit_url
from scrapers.circuits.models.services.normalization import (
    extract_coordinates_and_loc_norm,
)
from scrapers.circuits.models.services.normalization import extract_fia_grade
from scrapers.circuits.models.services.normalization import extract_history_events
from scrapers.circuits.models.services.normalization import extract_infobox_layouts
from scrapers.circuits.models.services.normalization import find_layout_for_table
from scrapers.circuits.models.services.normalization import loc_sort_key
from scrapers.circuits.models.services.normalization import merge_tables_into_layouts
from scrapers.circuits.models.services.normalization import parse_table_layout_info

__all__ = [
    "CircuitService",
    "LAYOUT_LENGTH_TOLERANCE_KM",
    "TOP_LEVEL_KEYS",
    "normalize_entity_value",
    "normalize_lap_record",
    "build_core_key",
    "is_record_subset",
    "is_empty_or_missing_value",
    "are_subset_values_compatible",
    "same_time_value",
    "same_dict_text_value",
    "select_best_date_year",
    "series_candidate",
    "select_best_series",
    "collect_other_fields",
    "merge_two_records",
    "merge_best_entity",
    "first_present_value",
    "merge_time",
    "merge_date_or_year",
    "merge_series",
    "fill_missing_fields_from_extra",
    "merge_record_group",
    "stage_a_partition_by_record_key",
    "stage_b_merge_by_core_key",
    "stage_c_merge_by_driver_time",
    "stage_d_fallback_merge_by_time_and_driver",
    "merge_race_lap_records",
    "extract_year_from_event",
    "extract_year",
    "normalize_lap_record_entity",
    "parse_lap_record_time_from_record",
    "has_meaningful_value",
    "select_best_field_with_url",
    "build_lap_record_key",
    "extract_circuit_names",
    "extract_circuit_url",
    "add_place",
    "loc_sort_key",
    "add_places_from_raw_location",
    "add_places_from_raw_dict",
    "add_places_from_raw_list",
    "extract_coordinates_and_loc_norm",
    "add_places_from_loc_norm",
    "extract_circuit_location",
    "extract_fia_grade",
    "extract_history_events",
    "extract_infobox_layouts",
    "parse_table_layout_info",
    "find_layout_for_table",
    "merge_tables_into_layouts",
]
