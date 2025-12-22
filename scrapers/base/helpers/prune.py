from __future__ import annotations

from typing import Any


def prune_empty(
    obj: Any,
    *,
    drop_empty_lists: bool = True,
    drop_none: bool = True,
    drop_empty_dicts: bool = True,
    drop_url_none: bool = False,
) -> Any:
    def _should_skip(value: Any) -> bool:
        if drop_none and value is None:
            return True
        if drop_empty_lists and isinstance(value, list) and len(value) == 0:
            return True
        if drop_empty_dicts and isinstance(value, dict) and len(value) == 0:
            return True
        return False

    if isinstance(obj, dict):
        cleaned: dict[str, Any] = {}
        for key, value in obj.items():
            if drop_url_none and key == "url" and value is None:
                continue
            pruned = prune_empty(
                value,
                drop_empty_lists=drop_empty_lists,
                drop_none=drop_none,
                drop_empty_dicts=drop_empty_dicts,
                drop_url_none=drop_url_none,
            )
            if _should_skip(pruned):
                continue
            cleaned[key] = pruned
        return cleaned

    if isinstance(obj, list):
        cleaned_list: list[Any] = []
        for item in obj:
            pruned = prune_empty(
                item,
                drop_empty_lists=drop_empty_lists,
                drop_none=drop_none,
                drop_empty_dicts=drop_empty_dicts,
                drop_url_none=drop_url_none,
            )
            if _should_skip(pruned):
                continue
            cleaned_list.append(pruned)
        return cleaned_list

    return obj
