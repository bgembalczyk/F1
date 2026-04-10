from __future__ import annotations

import ast
from pathlib import Path

TRANSITION_MODULE = Path("scrapers/services/domain_record/legacy_domain_record_service_alias.py")


def _find_forbidden_aliases(file_path: Path) -> list[int]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    lines: list[int] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DomainRecordService":
                    lines.append(node.lineno)
    return lines


def test_domain_record_service_alias_is_allowed_only_in_transition_module() -> None:
    root = Path("scrapers/services/domain_record")
    offenders: list[str] = []

    for file_path in sorted(root.glob("*.py")):
        if file_path == TRANSITION_MODULE:
            continue
        lines = _find_forbidden_aliases(file_path)
        if lines:
            offenders.append(f"{file_path}:{','.join(map(str, lines))}")

    assert not offenders, (
        "Found forbidden `DomainRecordService = ...` aliases outside transition module: "
        + "; ".join(offenders)
    )
