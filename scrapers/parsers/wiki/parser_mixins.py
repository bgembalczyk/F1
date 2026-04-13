from __future__ import annotations

from collections.abc import Iterable

from bs4 import Tag


class HeaderNormalizationMixin:
    """Shared header normalization for wiki table/infobox parsing."""

    @staticmethod
    def normalize_header(value: str) -> str:
        return " ".join(value.strip().lower().split())

    def normalize_headers(self, headers: Iterable[str]) -> list[str]:
        return [self.normalize_header(header) for header in headers if header.strip()]


class TableCellExtractionMixin:
    """Shared extraction for immediate child cells from a row."""

    @staticmethod
    def extract_row_cells(row: Tag) -> list[Tag]:
        return [
            cell
            for cell in row.find_all(["td", "th"], recursive=False)
            if isinstance(cell, Tag)
        ]


class NestedSectionHandlingMixin:
    """Backward-compat shim: filter_child_tags is now in RecursiveSectionParser."""

    @staticmethod
    def filter_child_tags(elements: Iterable[object]) -> list[Tag]:
        return [element for element in elements if isinstance(element, Tag)]
