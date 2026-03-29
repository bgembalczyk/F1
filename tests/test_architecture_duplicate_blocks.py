from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ENTRYPOINT_MODULES = (
    "scrapers/drivers/entrypoint.py",
    "scrapers/constructors/entrypoint.py",
    "scrapers/circuits/entrypoint.py",
    "scrapers/seasons/entrypoint.py",
    "scrapers/grands_prix/entrypoint.py",
)


def _collect_config_assignment_fingerprints() -> dict[str, list[str]]:
    fingerprints: dict[str, list[str]] = defaultdict(list)
    for py_file in Path("scrapers").rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "CONFIG"
                for target in node.targets
            ):
                continue
            normalized = ast.dump(node.value, include_attributes=False)
            fingerprints[normalized].append(f"{py_file}:{node.lineno}")
    return fingerprints


def test_no_duplicate_config_blocks() -> None:
    duplicates = {
        fp: locations
        for fp, locations in _collect_config_assignment_fingerprints().items()
        if len(locations) > 1
    }
    assert not duplicates, (
        "Duplicate CONFIG blocks detected. Extract shared config factory/base instead. "
        f"duplicates={duplicates}"
    )


def test_domain_entrypoints_use_shared_factory_builders() -> None:
    for path_str in ENTRYPOINT_MODULES:
        py_file = Path(path_str)
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))

        assert "install_domain_entrypoint" in source

        local_dups = [
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name in {"run_list_scraper", "__getattr__"}
        ]
        assert not local_dups, (
            "Entrypoint should not duplicate local wrappers. "
            "Use shared domain facade installer from scrapers.base.domain_entrypoint instead: "
            f"{py_file}"
        )
