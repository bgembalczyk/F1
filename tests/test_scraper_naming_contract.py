from __future__ import annotations

import ast
from pathlib import Path


def _iter_python_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*.py") if path.is_file()]


def test_scraper_suffix_classes_do_not_inherit_table_parser() -> None:
    """
    Klasy z sufiksem `Scraper` muszą implementować pipeline fetch/parse,
    więc nie mogą być parserami elementów HTML.
    """
    repo_root = Path(__file__).resolve().parents[1]
    scraper_files = _iter_python_files(repo_root / "scrapers")

    violations: list[str] = []
    for py_file in scraper_files:
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not node.name.endswith("Scraper"):
                continue
            base_names = {ast.unparse(base).split(".")[-1] for base in node.bases}
            if "TableParser" in base_names:
                relative = py_file.relative_to(repo_root)
                violations.append(f"{relative}:{node.lineno}:{node.name}")

    assert not violations, (
        "Klasy kończące się na `Scraper` nie mogą dziedziczyć po parserach tabel: "
        + ", ".join(sorted(violations))
    )
