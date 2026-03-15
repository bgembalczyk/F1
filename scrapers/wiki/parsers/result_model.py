from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

TOP_SECTION_NAME = "(Top)"

ParserMeta = dict[str, Any]
ParserResultItem = dict[str, Any]


def build_meta(
    *,
    section_id: str,
    heading_id: str | None,
    heading_path: list[str],
    position: int,
) -> ParserMeta:
    return {
        "section_id": section_id,
        "heading_id": heading_id,
        "heading_path": heading_path,
        "position": position,
    }


def build_result_item(item_type: str, data: Mapping[str, Any], meta: ParserMeta) -> ParserResultItem:
    return {
        "type": item_type,
        "meta": deepcopy(meta),
        "data": dict(data),
    }


def split_section_meta(
    section_name: str,
    parent_heading_path: list[str],
) -> tuple[str, str | None, list[str]]:
    heading_id = section_name if section_name != TOP_SECTION_NAME else None
    heading_path = [*parent_heading_path, section_name]
    section_id = section_name
    return section_id, heading_id, heading_path


def to_legacy_element(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": item["type"],
        "data": deepcopy(item["data"]),
    }


def to_legacy_section(item: Mapping[str, Any], child_key: str) -> dict[str, Any]:
    data = item["data"]
    return {
        "name": item["meta"]["section_id"],
        child_key: deepcopy(data.get(child_key, [])),
    }
