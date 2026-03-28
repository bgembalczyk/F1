from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from typing import TypedDict

from bs4 import Tag


class ArticleTableModel(TypedDict, total=False):
    headers: list[str]
    rows: list[dict[str, str]]
    caption: str
    heading_path: list[str]
    table_type: str
    _table: Tag


REQUIRED_ARTICLE_TABLE_KEYS = ("headers", "rows")


def ensure_article_table_model(payload: Mapping[str, Any]) -> ArticleTableModel:
    """Validate minimal article-table contract and return typed structure."""
    for key in REQUIRED_ARTICLE_TABLE_KEYS:
        if key not in payload:
            msg = f"Article table contract violation: missing key '{key}'"
            raise ValueError(msg)

    headers = payload["headers"]
    rows = payload["rows"]

    if not isinstance(headers, list) or not all(
        isinstance(header, str) for header in headers
    ):
        msg = "Article table contract violation: 'headers' must be list[str]"
        raise TypeError(msg)

    if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
        msg = "Article table contract violation: 'rows' must be list[mapping]"
        raise TypeError(msg)

    normalized: ArticleTableModel = {
        "headers": list(headers),
        "rows": [dict(row) for row in rows],
    }

    caption = payload.get("caption")
    if isinstance(caption, str) and caption.strip():
        normalized["caption"] = caption

    heading_path = payload.get("heading_path")
    if isinstance(heading_path, list) and all(isinstance(h, str) for h in heading_path):
        normalized["heading_path"] = list(heading_path)

    table_type = payload.get("table_type")
    if isinstance(table_type, str):
        normalized["table_type"] = table_type

    source_table = payload.get("_table")
    if isinstance(source_table, Tag):
        normalized["_table"] = source_table

    return normalized
