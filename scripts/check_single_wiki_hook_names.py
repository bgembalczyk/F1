from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

_BOOTSTRAP_PATH = Path(__file__).resolve().parent / "lib" / "bootstrap.py"
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "_scripts_bootstrap",
    _BOOTSTRAP_PATH,
)
assert _BOOTSTRAP_SPEC and _BOOTSTRAP_SPEC.loader
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)

REPO_ROOT = _BOOTSTRAP_MODULE.ensure_repo_root_on_sys_path()

from scripts.lib.check_runner import iter_python_paths
from scripts.lib.check_runner import run_cli

SCRAPERS_DIR = REPO_ROOT / "scrapers"

STANDARD_HOOK_NAMES = {
    "_build_infobox_payload",
    "_build_tables_payload",
    "_build_sections_payload",
    "_assemble_record",
}
HOOK_BASE_CLASSES = {
    "SingleWikiArticleScraperBase",
    "SingleWikiArticleSectionAdapterBase",
}


def _base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def _is_hook_alias(method_name: str) -> bool:
    payload_alias = (
        "payload" in method_name
        and any(token in method_name for token in ("infobox", "tables", "sections"))
        and method_name not in STANDARD_HOOK_NAMES
    )
    assemble_alias = (
        "assemble_record" in method_name and method_name not in STANDARD_HOOK_NAMES
    )
    return payload_alias or assemble_alias


def _has_allow_comment(source_lines: list[str], lineno: int) -> bool:
    start = max(0, lineno - 3)
    window = source_lines[start:lineno]
    return any("hook-name-allow:" in line for line in window)


def lint_path(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))
    errors: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        base_names = {_base_name(base) for base in node.bases}
        if not base_names.intersection(HOOK_BASE_CLASSES):
            continue

        for method in node.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            if not _is_hook_alias(method.name):
                continue
            if _has_allow_comment(source_lines, method.lineno):
                continue
            errors.append(
                f"{path}:{method.lineno} "
                f"unsupported hook alias '{method.name}' "
                f"(allowed: {', '.join(sorted(STANDARD_HOOK_NAMES))})",
            )

    return errors


def run_check(argv: list[str] | None = None) -> list[str]:
    targets = [Path(arg) for arg in argv] if argv else [SCRAPERS_DIR]
    errors: list[str] = []
    for path in iter_python_paths(targets):
        errors.extend(lint_path(path))
    return errors


def main(argv: list[str] | None = None) -> int:
    return run_cli("single-wiki-hook-names", lambda: run_check(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
