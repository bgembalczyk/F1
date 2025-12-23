"""Funkcje pomocnicze do scalania rekordów okrążeń."""

import re
from typing import Any

from scrapers.base.helpers.text_normalization import (
    match_driver_loose,
    match_vehicle_prefix,
)
from scrapers.base.helpers.time import (
    normalize_time_value,
    parse_time_key,
    parse_time_seconds_from_text,
)
from scrapers.base.helpers.value_objects import NormalizedDate

from models.services.circuits.lap_record_utils import (
    build_lap_record_key,
    parse_lap_record_time_from_record,
    select_best_field_with_url,
    normalize_lap_record_entity,
)


def _normalize_entity_value(value: Any) -> dict[str, Any] | None:
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

    driver = _normalize_entity_value(record.get("driver"))
    if driver is not None:
        record["driver"] = driver
    else:
        record.pop("driver", None)

    vehicle_value = record.get("vehicle") or record.get("car")
    vehicle = _normalize_entity_value(vehicle_value)
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
    series = _normalize_entity_value(series_value)
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


def extract_year_from_event(rec: dict[str, Any]) -> str | None:
    """
    Fallback dla rekordów tabelarycznych, które nie mają `year` ani `date`,
    ale mają `event` (np. "1963 Aintree 200", url: ".../1963_Aintree_200").
    """
    event = rec.get("event")
    candidates: list[str] = []

    if isinstance(event, dict):
        if event.get("text"):
            candidates.append(str(event["text"]))
        if event.get("url"):
            candidates.append(str(event["url"]))
    elif isinstance(event, str):
        candidates.append(event)

    year_re = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
    for s in candidates:
        m = year_re.search(s)
        if m:
            return m.group(1)

    return None


def _extract_year(rec: dict[str, Any]) -> str | None:
    """
    Wspólna logika ekstrakcji roku z rekordu.
    Próbuje kolejno: year, date.iso, event.
    """
    if rec.get("year") is not None:
        return str(rec["year"])

    date_obj = rec.get("date")
    if isinstance(date_obj, dict):
        iso = (date_obj.get("iso") or "").strip()
        if iso:
            return iso[:4]
    if isinstance(date_obj, NormalizedDate):
        iso = (date_obj.iso or "").strip()
        if iso:
            return iso[:4]

    return extract_year_from_event(rec)


def _extract_driver_vehicle_year(
    rec: dict[str, Any],
) -> tuple[str | None, str | None, str | None]:
    """
    Wspólna logika ekstrakcji driver_text, vehicle_text, year.
    Używana przez build_record_key i build_core_key.
    """
    driver_txt = normalize_lap_record_entity(rec.get("driver"))
    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = normalize_lap_record_entity(vehicle_obj)
    year = _extract_year(rec)

    return driver_txt, vehicle_txt, year


def build_record_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz do rozpoznawania tego samego rekordu:
    (driver_text, vehicle_text, year, time_seconds)
    """
    return build_lap_record_key(
        rec,
        year_extractor=_extract_year,
        key_order=("driver", "vehicle", "year", "time"),
    )


def build_core_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz „rdzeniowy" do łączenia rekordów nawet jeśli brakuje time.
    (driver_text, vehicle_text, year)
    """
    driver_txt, vehicle_txt, year = _extract_driver_vehicle_year(rec)

    if not driver_txt or not vehicle_txt or not year:
        return None

    return driver_txt, vehicle_txt, year


def is_record_subset(small: dict[str, Any], big: dict[str, Any]) -> bool:
    """
    True, jeśli small nie wnosi sprzecznych danych względem big.
    Używamy tylko do bezpiecznego fallback-merge.
    """
    for k, sv in small.items():
        if sv is None:
            continue
        if k not in big or big.get(k) is None:
            continue

        bv = big.get(k)

        if k == "time":
            st = parse_time_seconds_from_text(sv)
            bt = parse_time_seconds_from_text(bv)
            if st is None or bt is None:
                continue
            if round(float(st), 6) != round(float(bt), 6):
                return False
            continue

        if k == "driver":
            if not match_driver_loose(sv, bv):
                return False
            continue
        if k in ("vehicle", "car"):
            if not match_vehicle_prefix(sv, bv, min_len=6):
                return False
            continue

        if isinstance(sv, dict) and isinstance(bv, dict):
            stxt = (sv.get("text") or sv.get("name") or "").strip().lower()
            btxt = (bv.get("text") or bv.get("name") or "").strip().lower()
            if stxt and btxt and stxt != btxt:
                return False
            continue

        if sv != bv:
            return False

    return True


def select_best_driver(records: list[dict[str, Any]]) -> Any:
    """Wybiera najlepszy rekord kierowcy (preferuje wersję z URL)."""
    return select_best_field_with_url(records, "driver")


def select_best_vehicle(records: list[dict[str, Any]]) -> Any:
    """Wybiera najlepszy rekord pojazdu (preferuje wersję z URL)."""
    return select_best_field_with_url(records, "vehicle", "car")


def select_best_time(records: list[dict[str, Any]]) -> float | None:
    """Zwraca czas WYŁĄCZNIE jako sekundy (float)."""
    for r in records:
        tk = parse_time_key(r)
        if isinstance(tk, (int, float)):
            return float(tk)

    for r in records:
        t = r.get("time")
        if isinstance(t, dict):
            sec = t.get("seconds")
            if isinstance(sec, (int, float)):
                return float(sec)
        if isinstance(t, (int, float)):
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
            iso_cur = (best_date.get("iso") if isinstance(best_date, dict) else "") or ""

        if isinstance(d, NormalizedDate):
            iso_new = d.iso or ""
        else:
            iso_new = (d.get("iso") if isinstance(d, dict) else "") or ""
        if len(iso_new) > len(iso_cur):
            best_date = d

    return best_date, best_year


def select_best_series(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Wybiera najlepszą serię/kategorię (preferuje wersję z linkiem)."""

    def series_candidate(record: dict[str, Any]) -> dict[str, Any] | None:
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
                "text": (
                    field_value.get("text") or field_value.get("name") or ""
                ).strip(),
                "url": field_value.get("url"),
            }
        return {"text": str(field_value).strip(), "url": None}

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


def merge_two_records(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Scala dwa rekordy w jeden, preferując bogatsze dane."""
    merged: dict[str, Any] = dict(base)

    for key in ("driver",):
        a = base.get(key)
        b = extra.get(key)
        if isinstance(a, dict) and a.get("url"):
            merged[key] = a
        elif b is not None:
            merged[key] = b

    a_v = base.get("vehicle") or base.get("car")
    b_v = extra.get("vehicle") or extra.get("car")
    if isinstance(a_v, dict) and a_v.get("url"):
        merged["vehicle"] = a_v
    elif b_v is not None:
        merged["vehicle"] = b_v

    t = parse_lap_record_time_from_record(base)
    if t is None:
        t = parse_lap_record_time_from_record(extra)
    if t is not None:
        merged["time"] = float(t)
    merged.pop("time_seconds", None)

    best_date, best_year = select_best_date_year([base, extra])
    if best_year is None:
        best_year = extract_year_from_event(base) or extract_year_from_event(extra)

    if best_date is not None:
        merged["date"] = best_date
        merged.pop("year", None)
    elif best_year is not None:
        merged["year"] = best_year

    best_series = select_best_series([base, extra])
    if best_series is not None:
        merged["series"] = best_series
    merged.pop("category", None)
    merged.pop("class", None)
    merged.pop("class_", None)

    for k, v in extra.items():
        if k in {"time_seconds", "category", "class", "class_"}:
            continue
        if merged.get(k) is None and v is not None:
            merged[k] = v

    return merged


def merge_record_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Scal grupę rekordów do jednego."""
    merged = collect_other_fields(records)

    best_driver = select_best_driver(records)
    best_vehicle = select_best_vehicle(records)
    best_date, best_year = select_best_date_year(records)
    best_series = select_best_series(records)

    t = None
    for r in records:
        t = parse_lap_record_time_from_record(r)
        if t is not None:
            break

    if best_year is None:
        for r in records:
            y = extract_year_from_event(r)
            if y:
                best_year = y
                break

    if best_driver is not None:
        merged["driver"] = best_driver
    if best_vehicle is not None:
        merged["vehicle"] = best_vehicle
    if t is not None:
        merged["time"] = float(t)

    if best_date is not None:
        merged["date"] = best_date
    elif best_year is not None:
        merged["year"] = best_year

    if best_series is not None:
        merged["series"] = best_series

    return merged


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
        k = build_record_key(rec)
        if k is None:
            leftovers.append(rec)
        else:
            key_buckets.setdefault(k, []).append(rec)

    return key_buckets, leftovers


def _stage_b_merge_by_core_key(
    merged_main: list[dict[str, Any]], leftovers: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap B: Merge po core_key (driver+vehicle+year) – łączy rekordy nawet bez time.
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
                    float(rec_t), 6
                ):
                    chosen_idx = idx
                    break

        if chosen_idx is None:
            chosen_idx = cand_ids[0]

        merged_main[chosen_idx] = merge_two_records(merged_main[chosen_idx], rec)

    return merged_main, still_left


def _stage_c_merge_by_driver_time(
    merged_main: list[dict[str, Any]], still_left: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap C: Merge po (driver+time) z prefixem vehicle – dla uciętych vehicle.
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
    merged_main: list[dict[str, Any]], final_left: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Etap D: Fallback merge po (time) z walidacją driver + subset – ostatnia szansa.
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
                rec.get("driver"), target.get("driver")
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
    - B: merge po core_key (driver+vehicle+year) – pozwala łączyć brakujące time.
    - C: merge po (driver+time) z prefixem vehicle – dla uciętych vehicle.
    - D: fallback merge po (time) z walidacją – ostatnia szansa.
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
        merged_main, final_left
    )

    return merged_main + last_left
