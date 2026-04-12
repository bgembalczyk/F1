from __future__ import annotations

from typing import Any
from typing import TypedDict


class SectionTreeNode(TypedDict, total=False):
    section_id: str
    section_label: str
    heading_anchor: str
    elements: list[dict[str, Any]]
    sub_sections: list["SectionTreeNode"]
    sub_sub_sections: list["SectionTreeNode"]
    sub_sub_sub_sections: list["SectionTreeNode"]


class SectionTreePayload(TypedDict, total=False):
    sub_sections: list[SectionTreeNode]
    sub_sub_sections: list[SectionTreeNode]
    sub_sub_sub_sections: list[SectionTreeNode]
    elements: list[dict[str, Any]]
    items: list[dict[str, Any]]


__all__ = ["SectionTreeNode", "SectionTreePayload"]
