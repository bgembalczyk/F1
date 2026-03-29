from __future__ import annotations

from typing import TYPE_CHECKING

from tests.architecture.rules import ParsedImport
from tests.architecture.rules import parse_imports as parse_imports_from_rules

if TYPE_CHECKING:
    from pathlib import Path


def parse_imports(py_file: Path) -> list[ParsedImport]:
    """Backward-compatible shim for legacy imports.

    Canonical source of truth lives in ``tests.architecture.rules``.
    """

    return parse_imports_from_rules(py_file)
