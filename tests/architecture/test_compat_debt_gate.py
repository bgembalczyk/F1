from __future__ import annotations

import ast
from pathlib import Path

from tests.architecture.helpers import count_compat_debt_imports
from tests.architecture.helpers import count_record_factory_aliases
from tests.architecture.helpers import iter_python_files

MAX_COMPAT_IMPORTS_BY_FILE: dict[str, int] = {
    "models/records/factories/base.py": 1,
    "models/records/factories/mapping.py": 1,
    "scrapers/module_naming_aliases.py": 3,
}

MAX_RECORD_FACTORY_ALIAS_BY_FILE: dict[str, int] = {
    "models/records/factories/protocol2.py": 1,
}


def test_compat_debt_imports_do_not_grow() -> None:
    violations: list[str] = []
    for py_file in iter_python_files():
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        rel = py_file.as_posix()
        count = count_compat_debt_imports(tree)
        allowed = MAX_COMPAT_IMPORTS_BY_FILE.get(rel, 0)
        if count > allowed:
            violations.append(
                f"{rel}: compat debt imports={count}, allowed max={allowed}",
            )

    assert not violations, "\n".join(violations)


def test_record_factory_aliases_do_not_grow() -> None:
    violations: list[str] = []
    for py_file in iter_python_files():
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        rel = py_file.as_posix()
        count = count_record_factory_aliases(tree)
        allowed = MAX_RECORD_FACTORY_ALIAS_BY_FILE.get(rel, 0)
        if count > allowed:
            violations.append(
                f"{rel}: RecordFactory aliases={count}, allowed max={allowed}",
            )

    assert not violations, "\n".join(violations)
