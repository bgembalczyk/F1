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
            if drop_none and pruned is None:
                continue
            if drop_empty_lists and isinstance(pruned, list) and len(pruned) == 0:
                continue
            if drop_empty_dicts and isinstance(pruned, dict) and len(pruned) == 0:
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
            if drop_none and pruned is None:
                continue
            if drop_empty_lists and isinstance(pruned, list) and len(pruned) == 0:
                continue
            if drop_empty_dicts and isinstance(pruned, dict) and len(pruned) == 0:
                continue
            cleaned_list.append(pruned)
        return cleaned_list

    return obj
