"""Record keying and merging helpers for lap record data."""

from __future__ import annotations

from typing import Any
import re

from scrapers.base.helpers.text import (
    match_driver_loose,
    match_vehicle_prefix,
    normalize_text,
)
from scrapers.base.helpers.time import parse_time_key, parse_time_seconds

_YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


def parse_event_year(rec: dict[str, Any]) -> str | None:
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

    for s in candidates:
        m = _YEAR_RE.search(s)
        if m:
            return m.group(1)

    return None


def build_record_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz do rozpoznawania tego samego rekordu:

    (driver_text, vehicle_text, year, time_seconds)
    """
    driver_txt = normalize_text(rec.get("driver"))

    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = normalize_text(vehicle_obj)

    year: str | None = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = parse_event_year(rec)

    time_sec = parse_time_seconds(rec)

    if not driver_txt or not vehicle_txt or not year or time_sec is None:
        return None

    return (driver_txt, vehicle_txt, year, round(time_sec, 6))


def build_core_key(rec: dict[str, Any]) -> tuple | None:
    """
    Klucz „rdzeniowy" do łączenia rekordów nawet jeśli brakuje time.

    (driver_text, vehicle_text, year)
    """
    driver_txt = normalize_text(rec.get("driver"))
    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = normalize_text(vehicle_obj)

    year: str | None = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = parse_event_year(rec)

    if not driver_txt or not vehicle_txt or not year:
        return None

    return (driver_txt, vehicle_txt, year)


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
            st = parse_time_seconds(
                {"time": sv} if not isinstance(sv, dict) else {"time": sv}
            )
            bt = parse_time_seconds(
                {"time": bv} if not isinstance(bv, dict) else {"time": bv}
            )
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


def merge_two_records(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """
    Scala dwa rekordy w jeden, preferując bogatsze dane:
    - driver/vehicle: preferuj dict z url
    - series: wybierz najlepsze przez select_best_series([..])
    - date/year: wybierz najlepsze przez select_best_date_and_year([..]) + fallback z event
    - event/pozostałe: pierwszy niepusty
    - time: zawsze float w sekundach
    """
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

    t = parse_time_seconds(base)
    if t is None:
        t = parse_time_seconds(extra)
    if t is not None:
        merged["time"] = float(t)
    merged.pop("time_seconds", None)

    best_date, best_year = select_best_date_and_year([base, extra])
    if best_year is None:
        best_year = parse_event_year(base) or parse_event_year(extra)

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


def collect_other_fields(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Zbiera pozostałe pola, ale NIE przenosi dubli typu:
    - time_seconds (bo wynikowo i tak będzie time w sekundach)
    - category/class (bo wynikowo i tak będzie series)
    """
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


def select_best_driver(records: list[dict[str, Any]]) -> Any:
    """Wybiera najlepszy rekord kierowcy (preferuje wersję z URL)."""
    best = None
    for r in records:
        d = r.get("driver")
        if not d:
            continue
        if best is None:
            best = d
            continue
        if (
            isinstance(d, dict)
            and d.get("url")
            and (not isinstance(best, dict) or not best.get("url"))
        ):
            best = d
    return best


def select_best_vehicle(records: list[dict[str, Any]]) -> Any:
    """Wybiera najlepszy rekord pojazdu (preferuje wersję z URL)."""
    best = None
    for r in records:
        v = r.get("vehicle") or r.get("car")
        if not v:
            continue
        if best is None:
            best = v
            continue
        if (
            isinstance(v, dict)
            and v.get("url")
            and (not isinstance(best, dict) or not best.get("url"))
        ):
            best = v
    return best


def select_best_time(records: list[dict[str, Any]]) -> float | None:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float).
    """
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


def select_best_date_and_year(records: list[dict[str, Any]]) -> tuple[Any, Any]:
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

        iso_cur = (best_date.get("iso") if isinstance(best_date, dict) else "") or ""
        iso_new = (d.get("iso") if isinstance(d, dict) else "") or ""
        if len(iso_new) > len(iso_cur):
            best_date = d

    return best_date, best_year


def select_best_series(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Wybiera najlepszą serię/kategorię (preferuje wersję z linkiem)."""

    def series_candidate(r: dict[str, Any]) -> dict[str, Any] | None:
        cand = r.get("series") or r.get("category") or r.get("class") or r.get("class_")
        if cand is None:
            return None
        if isinstance(cand, dict):
            return {
                "text": (cand.get("text") or cand.get("name") or "").strip(),
                "url": cand.get("url"),
            }
        return {"text": str(cand).strip(), "url": None}

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


def merge_record_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Wynik:
    - time: float (sekundy)
    - series: dict{text,url}
    - year: jeśli brak date, bierzemy year (również z event)
    """
    merged = collect_other_fields(records)

    best_driver = select_best_driver(records)
    best_vehicle = select_best_vehicle(records)
    best_date, best_year = select_best_date_and_year(records)
    best_series = select_best_series(records)

    t = None
    for r in records:
        t = parse_time_seconds(r)
        if t is not None:
            break

    if best_year is None:
        for r in records:
            y = parse_event_year(r)
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


def merge_race_lap_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Łączy duplikujące się rekordy (infobox + tabela) w jeden bogaty rekord.
    """
    key_buckets: dict[tuple, list[dict[str, Any]]] = {}
    leftovers: list[dict[str, Any]] = []

    for rec in records:
        k = build_record_key(rec)
        if k is None:
            leftovers.append(rec)
        else:
            key_buckets.setdefault(k, []).append(rec)

    merged_main: list[dict[str, Any]] = [
        merge_record_group(rs) for rs in key_buckets.values()
    ]

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

        rec_t = parse_time_seconds(rec)
        chosen_idx = None
        if rec_t is not None:
            for idx in cand_ids:
                tgt_t = parse_time_seconds(merged_main[idx])
                if tgt_t is not None and round(float(tgt_t), 6) == round(
                    float(rec_t), 6
                ):
                    chosen_idx = idx
                    break

        if chosen_idx is None:
            chosen_idx = cand_ids[0]

        merged_main[chosen_idx] = merge_two_records(merged_main[chosen_idx], rec)

    index_dt: dict[tuple, list[int]] = {}
    for i, rec in enumerate(merged_main):
        d = normalize_text(rec.get("driver"))
        t = parse_time_seconds(rec)
        if d and t is not None:
            index_dt.setdefault((d, round(float(t), 6)), []).append(i)

    final_left: list[dict[str, Any]] = []
    for rec in still_left:
        d = normalize_text(rec.get("driver"))
        t = parse_time_seconds(rec)
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

    time_index: dict[float, list[int]] = {}
    for i, rec in enumerate(merged_main):
        t = parse_time_seconds(rec)
        if t is None:
            continue
        time_index.setdefault(round(float(t), 6), []).append(i)

    last_left: list[dict[str, Any]] = []
    for rec in final_left:
        t = parse_time_seconds(rec)
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

    return merged_main + last_left
