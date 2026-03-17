"""Funkcje pomocnicze do scalania rekordów okrążeń."""

from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.text_normalization import match_driver_loose
from scrapers.base.helpers.text_normalization import match_vehicle_prefix
from scrapers.base.helpers.time import normalize_time_value
from scrapers.base.helpers.time import parse_time_key
from scrapers.base.helpers.time import parse_time_seconds_from_text
from scrapers.circuits.models.services.lap_record_utils import build_lap_record_key
from scrapers.circuits.models.services.lap_record_utils import extract_year
from scrapers.circuits.models.services.lap_record_utils import extract_year_from_event
from scrapers.circuits.models.services.lap_record_utils import (
    normalize_lap_record_entity,
)
from scrapers.circuits.models.services.lap_record_utils import (
    parse_lap_record_time_from_record,
)
from scrapers.circuits.models.services.lap_record_utils import (
    select_best_field_with_url,
)


def normalize_entity_value(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        text = (value.get("text") or value.get("name") or "").strip()
        url = value.get("url")
        if not text and not url:
            return None
        return {"text": text, "url": url}
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return {"text": text, "url": None}
    return None


def normalize_lap_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalizuje rekord okrążenia (driver/vehicle/series oraz czas)."""
    if not record:
        return record

    if record.get("driver") is None and record.get("driver_rider") is not None:
        record["driver"] = record.get("driver_rider")

    driver = normalize_entity_value(record.get("driver"))
    if driver is not None:
        record["driver"] = driver
    else:
        record.pop("driver", None)

    vehicle_value = record.get("vehicle") or record.get("car")
    vehicle = normalize_entity_value(vehicle_value)
    if vehicle is not None:
        record["vehicle"] = vehicle
    else:
        record.pop("vehicle", None)
    record.pop("car", None)

    series_value = (
        record.get("series")
        or record.get("category")
        or record.get("class")
        or record.get("class_")
    )
    series = normalize_entity_value(series_value)
    if series is not None:
        record["series"] = series
    else:
        record.pop("series", None)
    record.pop("category", None)
    record.pop("class", None)
    record.pop("class_", None)

    normalize_time_value(record)
    time_seconds = parse_lap_record_time_from_record(record)
    if time_seconds is not None:
        record["time"] = float(time_seconds)
    record.pop("time_seconds", None)

    record.pop("driver_rider", None)

    return record


def build_core_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz „rdzeniowy" do łączenia rekordów nawet jeśli brakuje time.
    (driver_text, vehicle_text, year)
    """
    driver_txt = normalize_lap_record_entity(rec.get("driver"))
    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = normalize_lap_record_entity(vehicle_obj)
    year = extract_year(rec)

    if not driver_txt or not vehicle_txt or not year:
        return None

    return driver_txt, vehicle_txt, year


def is_record_subset(
    small: dict[str, Any],
    big: dict[str, Any],
) -> bool:
    """
    True, jeśli small nie wnosi sprzecznych danych względem big.
    Używamy tylko do bezpiecznego fallback-merge.
    """
    for key, small_value in small.items():
        if _is_empty_or_missing_value(key, small_value, big):
            continue
        big_value = big.get(key)
        if not _are_subset_values_compatible(key, small_value, big_value):
            return False
    return True


def _is_empty_or_missing_value(
    key: str,
    small_value: Any,
    big: dict[str, Any],
) -> bool:
    return small_value is None or key not in big or big.get(key) is None


def _are_subset_values_compatible(key: str, small_value: Any, big_value: Any) -> bool:
    if key == "time":
        return _same_time_value(small_value, big_value)
    if key == "driver":
        return match_driver_loose(small_value, big_value)
    if key in ("vehicle", "car"):
        return match_vehicle_prefix(small_value, big_value, min_len=6)
    if isinstance(small_value, dict) and isinstance(big_value, dict):
        return _same_dict_text_value(small_value, big_value)
    return small_value == big_value


def _same_time_value(small_value: Any, big_value: Any) -> bool:
    small_time = parse_time_seconds_from_text(small_value)
    big_time = parse_time_seconds_from_text(big_value)
    if small_time is None or big_time is None:
        return True
    return round(float(small_time), 6) == round(float(big_time), 6)


def _same_dict_text_value(
    small_value: dict[str, Any],
    big_value: dict[str, Any],
) -> bool:
    small_text = (
        (small_value.get("text") or small_value.get("name") or "").strip().lower()
    )
    big_text = (big_value.get("text") or big_value.get("name") or "").strip().lower()
    return not (small_text and big_text and small_text != big_text)


def select_best_time(records: list[dict[str, Any]]) -> float | None:
    """Zwraca czas WYŁĄCZNIE jako sekundy (float)."""
    for r in records:
        tk = parse_time_key(r)
        if isinstance(tk, int | float):
            return float(tk)

    for r in records:
        t = r.get("time")
        if isinstance(t, dict):
            sec = t.get("seconds")
            if isinstance(sec, int | float):
                return float(sec)
        if isinstance(t, int | float):
            return float(t)
        if isinstance(t, str):
            try:
                return float(t.strip())
            except ValueError:
                continue

    return None


def select_best_date_year(records: list[dict[str, Any]]) -> tuple[Any, Any]:
    """Wybiera najlepszą datę i rok (preferuje dokładniejszy iso)."""
    best_date = None
    best_year = None

    for r in records:
        if best_year is None and r.get("year") is not None:
            best_year = r.get("year")

        d = r.get("date")
        if not d:
            continue
        if best_date is None:
            best_date = d
            continue

        if isinstance(best_date, NormalizedDate):
            iso_cur = best_date.iso or ""
        else:
            iso_cur = (
                best_date.get("iso") if isinstance(best_date, dict) else ""
            ) or ""

        if isinstance(d, NormalizedDate):
            iso_new = d.iso or ""
        else:
            iso_new = (d.get("iso") if isinstance(d, dict) else "") or ""
        if len(iso_new) > len(iso_cur):
            best_date = d

    return best_date, best_year


def series_candidate(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extrahuje kandydata serii/kategorii z rekordu."""
    field_value = (
        record.get("series")
        or record.get("category")
        or record.get("class")
        or record.get("class_")
    )
    if field_value is None:
        return None
    if isinstance(field_value, dict):
        return {
            "text": (field_value.get("text") or field_value.get("name") or "").strip(),
            "url": field_value.get("url"),
        }
    return {"text": str(field_value).strip(), "url": None}


def select_best_series(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Wybiera najlepszą serię/kategorię (preferuje wersję z linkiem)."""
    best = None
    best_has_url = False
    best_len = 0

    for r in records:
        cand = series_candidate(r)
        if not cand:
            continue

        text = (cand.get("text") or "").strip()
        has_url = bool(cand.get("url"))
        text_len = len(text)

        if best is None:
            best = cand
            best_has_url = has_url
            best_len = text_len
            continue

        if has_url and not best_has_url:
            best = cand
            best_has_url = True
            best_len = text_len
            continue

        if has_url == best_has_url and text_len > best_len:
            best = cand
            best_len = text_len

    return best


def collect_other_fields(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Zbiera pozostałe pola, bez przenoszenia dubli time_seconds/category/class."""
    ignore_keys = {
        "driver",
        "vehicle",
        "car",
        "time",
        "time_seconds",
        "date",
        "year",
        "series",
        "category",
        "class",
        "class_",
    }

    merged: dict[str, Any] = {}
    for r in records:
        for k, v in r.items():
            if k in ignore_keys:
                continue
            if k not in merged and v is not None:
                merged[k] = v
    return merged


def merge_two_records(
    base: dict[str, Any],
    extra: dict[str, Any],
) -> dict[str, Any]:
    """Scala dwa rekordy w jeden, preferując bogatsze dane."""
    merged: dict[str, Any] = dict(base)

    _merge_best_entity(
        merged,
        base,
        extra,
        target_key="driver",
        source_keys=("driver",),
    )
    _merge_best_entity(
        merged,
        base,
        extra,
        target_key="vehicle",
        source_keys=("vehicle", "car"),
    )
    _merge_time(merged, base, extra)
    _merge_date_or_year(merged, base, extra)
    _merge_series(merged, base, extra)
    _fill_missing_fields_from_extra(merged, extra)

    return merged


def _merge_best_entity(
    merged: dict[str, Any],
    base: dict[str, Any],
    extra: dict[str, Any],
    *,
    target_key: str,
    source_keys: tuple[str, ...],
) -> None:
    base_value = _first_present_value(base, source_keys)
    extra_value = _first_present_value(extra, source_keys)
    if isinstance(base_value, dict) and base_value.get("url"):
        merged[target_key] = base_value
    elif extra_value is not None:
        merged[target_key] = extra_value


def _first_present_value(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = record.get(key)
        if value is not None:
            return value
    return None


def _merge_time(
    merged: dict[str, Any],
    base: dict[str, Any],
    extra: dict[str, Any],
) -> None:
    parsed_time = parse_lap_record_time_from_record(base)
    if parsed_time is None:
        parsed_time = parse_lap_record_time_from_record(extra)
    if parsed_time is not None:
        merged["time"] = float(parsed_time)
    merged.pop("time_seconds", None)


def _merge_date_or_year(
    merged: dict[str, Any],
    base: dict[str, Any],
    extra: dict[str, Any],
) -> None:
    best_date, best_year = select_best_date_year([base, extra])
    if best_year is None:
        best_year = extract_year_from_event(base) or extract_year_from_event(extra)

    if best_date is not None:
        merged["date"] = best_date
        merged.pop("year", None)
    elif best_year is not None:
        merged["year"] = best_year


def _merge_series(
    merged: dict[str, Any],
    base: dict[str, Any],
    extra: dict[str, Any],
) -> None:
    best_series = select_best_series([base, extra])
    if best_series is not None:
        merged["series"] = best_series
    merged.pop("category", None)
    merged.pop("class", None)
    merged.pop("class_", None)


def _fill_missing_fields_from_extra(
    merged: dict[str, Any],
    extra: dict[str, Any],
) -> None:
    for key, value in extra.items():
        if key in {"time_seconds", "category", "class", "class_"}:
            continue
        if merged.get(key) is None and value is not None:
            merged[key] = value


def merge_record_group(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Scal grupę rekordów do jednego."""
    merged = collect_other_fields(records)

    _set_group_best_entities(merged, records)
    _set_group_best_time(merged, records)
    _set_group_best_date_or_year(merged, records)
    _set_group_best_series(merged, records)

    return merged


def _set_group_best_entities(
    merged: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    best_driver = select_best_field_with_url(records, "driver")
    best_vehicle = select_best_field_with_url(records, "vehicle", "car")
    if best_driver is not None:
        merged["driver"] = best_driver
    if best_vehicle is not None:
        merged["vehicle"] = best_vehicle


def _set_group_best_time(merged: dict[str, Any], records: list[dict[str, Any]]) -> None:
    for record in records:
        parsed_time = parse_lap_record_time_from_record(record)
        if parsed_time is not None:
            merged["time"] = float(parsed_time)
            return


def _set_group_best_date_or_year(
    merged: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    best_date, best_year = select_best_date_year(records)
    if best_year is None:
        best_year = _find_first_event_year(records)

    if best_date is not None:
        merged["date"] = best_date
    elif best_year is not None:
        merged["year"] = best_year


def _find_first_event_year(records: list[dict[str, Any]]) -> int | None:
    for record in records:
        year = extract_year_from_event(record)
        if year:
            return year
    return None


def _set_group_best_series(
    merged: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    best_series = select_best_series(records)
    if best_series is not None:
        merged["series"] = best_series


def _stage_a_partition_by_record_key(
    records: list[dict[str, Any]],
) -> tuple[dict[tuple, list[dict[str, Any]]], list[dict[str, Any]]]:
    """
    Etap A: Partycjonowanie rekordów po record_key (driver+vehicle+year+time).
    Zwraca buckety matching'owe i pozostałe rekordy.
    """
    key_buckets: dict[tuple, list[dict[str, Any]]] = {}
    leftovers: list[dict[str, Any]] = []

    for rec in records:
        k = build_lap_record_key(rec, year_extractor=extract_year)
        if k is None:
            leftovers.append(rec)
        else:
            key_buckets.setdefault(k, []).append(rec)

    return key_buckets, leftovers


def _stage_b_merge_by_core_key(
    merged_main: list[dict[str, Any]],
    leftovers: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap B: Merge po core_key (driver+vehicle+year) - łączy rekordy nawet bez time.
    Zwraca zaktualizowane merged_main i pozostałe rekordy.
    """
    core_index: dict[tuple, list[int]] = {}
    for i, rec in enumerate(merged_main):
        ck = build_core_key(rec)
        if ck is not None:
            core_index.setdefault(ck, []).append(i)

    still_left: list[dict[str, Any]] = []
    for rec in leftovers:
        ck = build_core_key(rec)
        if ck is None:
            still_left.append(rec)
            continue

        cand_ids = core_index.get(ck, [])
        if not cand_ids:
            still_left.append(rec)
            continue

        rec_t = parse_lap_record_time_from_record(rec)
        chosen_idx = None
        if rec_t is not None:
            for idx in cand_ids:
                tgt_t = parse_lap_record_time_from_record(merged_main[idx])
                if tgt_t is not None and round(float(tgt_t), 6) == round(
                    float(rec_t),
                    6,
                ):
                    chosen_idx = idx
                    break

        if chosen_idx is None:
            chosen_idx = cand_ids[0]

        merged_main[chosen_idx] = merge_two_records(merged_main[chosen_idx], rec)

    return merged_main, still_left


def _stage_c_merge_by_driver_time(
    merged_main: list[dict[str, Any]],
    still_left: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap C: Merge po (driver+time) z prefixem vehicle - dla uciętych vehicle.
    Zwraca zaktualizowane merged_main i pozostałe rekordy.
    """
    index_dt: dict[tuple, list[int]] = {}
    for i, rec in enumerate(merged_main):
        d = normalize_lap_record_entity(rec.get("driver"))
        t = parse_lap_record_time_from_record(rec)
        if d and t is not None:
            index_dt.setdefault((d, round(float(t), 6)), []).append(i)

    final_left: list[dict[str, Any]] = []
    for rec in still_left:
        d = normalize_lap_record_entity(rec.get("driver"))
        t = parse_lap_record_time_from_record(rec)
        if not d or t is None:
            final_left.append(rec)
            continue

        cand_ids = index_dt.get((d, round(float(t), 6)), [])
        if not cand_ids:
            final_left.append(rec)
            continue

        v = rec.get("vehicle") or rec.get("car")
        matched = False
        for idx in cand_ids:
            target = merged_main[idx]
            tv = target.get("vehicle") or target.get("car")
            if match_vehicle_prefix(v, tv, min_len=10):
                merged_main[idx] = merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            final_left.append(rec)

    return merged_main, final_left


def _stage_d_fallback_merge_by_time_and_driver(
    merged_main: list[dict[str, Any]],
    final_left: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap D: Fallback merge po (time) z walidacją driver + subset - ostatnia szansa.
    Zwraca zaktualizowane merged_main i ostatecznie pozostałe rekordy.
    """
    time_index: dict[float, list[int]] = {}
    for i, rec in enumerate(merged_main):
        t = parse_lap_record_time_from_record(rec)
        if t is None:
            continue
        time_index.setdefault(round(float(t), 6), []).append(i)

    last_left: list[dict[str, Any]] = []
    for rec in final_left:
        t = parse_lap_record_time_from_record(rec)
        if t is None:
            last_left.append(rec)
            continue

        cand_ids = time_index.get(round(float(t), 6), [])
        if not cand_ids:
            last_left.append(rec)
            continue

        matched = False
        for idx in cand_ids:
            target = merged_main[idx]

            if match_driver_loose(
                rec.get("driver"),
                target.get("driver"),
            ) and is_record_subset(rec, target):
                merged_main[idx] = merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            last_left.append(rec)

    return merged_main, last_left


def merge_race_lap_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Łączy duplikujące się rekordy (infobox + tabela) w jeden bogaty rekord.

    Etapy:
    - A: twardy merge po record_key (driver+vehicle+year+time).
    - B: merge po core_key (driver+vehicle+year) - pozwala łączyć brakujące time.
    - C: merge po (driver+time) z prefixem vehicle - dla uciętych vehicle.
    - D: fallback merge po (time) z walidacją - ostatnia szansa.
    """
    # Etap A: Partycjonowanie po record_key
    key_buckets, leftovers = _stage_a_partition_by_record_key(records)
    merged_main = [merge_record_group(rs) for rs in key_buckets.values()]

    # Etap B: Merge po core_key
    merged_main, still_left = _stage_b_merge_by_core_key(merged_main, leftovers)

    # Etap C: Merge po (driver+time) z prefixem vehicle
    merged_main, final_left = _stage_c_merge_by_driver_time(merged_main, still_left)

    # Etap D: Fallback merge po (time) z walidacją
    merged_main, last_left = _stage_d_fallback_merge_by_time_and_driver(
        merged_main,
        final_left,
    )

    return merged_main + last_left
