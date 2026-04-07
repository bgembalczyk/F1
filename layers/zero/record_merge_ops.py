from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar

from layers.zero.merge_types import DriverSeriesStats

if TYPE_CHECKING:
    from collections.abc import Callable


def merge_list_values(existing: list[object], incoming: list[object]) -> list[object]:
    merged = list(existing)
    seen = {
        json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
        for item in merged
    }
    for item in incoming:
        serialized = json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
        if serialized in seen:
            continue
        seen.add(serialized)
        merged.append(item)
    return merged


def merge_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = dict(existing)
        for key, value in incoming.items():
            if key in merged:
                merged[key] = merge_values(merged[key], value)
            else:
                merged[key] = value
        return merged

    if isinstance(existing, list) and isinstance(incoming, list):
        return merge_list_values(existing, incoming)

    if existing in (None, "", []):
        return incoming

    return existing


def merge_driver_dict_values(
    existing: dict[str, object],
    incoming: dict[str, object],
) -> dict[str, object]:
    normalized_incoming = DriverSeriesStats.from_dict(incoming).to_dict()
    merged = dict(existing)
    for key, value in normalized_incoming.items():
        if key in {"entries", "starts"}:
            continue
        if key in merged:
            merged[key] = merge_driver_values(merged[key], value)
        else:
            merged[key] = value
    return merged


def merge_driver_values(existing: object, incoming: object) -> object:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        return merge_driver_dict_values(existing, incoming)
    if isinstance(existing, list) and isinstance(incoming, list):
        return merge_list_values(existing, incoming)
    if existing in (None, "", []):
        return incoming
    return existing


class MergeModel(Protocol):
    @classmethod
    def from_object(cls, value: object) -> MergeModel | None: ...
    def dedupe_key(self) -> str | None: ...
    def to_dict(self) -> dict[str, Any]: ...


T = TypeVar("T", bound=MergeModel)


def _handle_new_record(
    model: MergeModel,
    merged_records: list[object],
    key_to_index: dict[str, int],
    key: str,
) -> None:
    index = len(merged_records)
    key_to_index[key] = index
    merged_records.append(model.to_dict())

    if hasattr(model, "aliases"):
        for alias in model.aliases():
            key_to_index[alias] = index


def merge_duplicate_records(
    records: list[object],
    model_cls: type[T],
    merge_func: Callable[[object, object], object],
) -> list[object]:
    merged_records: list[object] = []
    key_to_index: dict[str, int] = {}

    for record in records:
        model = model_cls.from_object(record)
        if model is None:
            merged_records.append(record)
            continue
        key = model.dedupe_key()
        if key is None:
            merged_records.append(model.to_dict())
            continue

        index = key_to_index.get(key)
        if index is None:
            _handle_new_record(model, merged_records, key_to_index, key)
            continue

        existing = merged_records[index]
        existing_model = model_cls.from_object(existing)
        if existing_model is None:
            continue

        merged_record = merge_func(existing_model.to_dict(), model.to_dict())
        merged_records[index] = merged_record

        if hasattr(model, "aliases"):
            merged_model = model_cls.from_object(merged_record)
            if merged_model is not None:
                for alias in merged_model.aliases():
                    key_to_index[alias] = index

    return merged_records
