from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

_BOOTSTRAP_PATH = Path(__file__).resolve().parents[1] / "lib" / "bootstrap.py"
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "_scripts_bootstrap",
    _BOOTSTRAP_PATH,
)
assert _BOOTSTRAP_SPEC
assert _BOOTSTRAP_SPEC.loader
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)

REPO_ROOT = _BOOTSTRAP_MODULE.ensure_repo_root_on_sys_path()
from scrapers.deprecation_catalog import get_deprecated_module_migrations

DOC_PATH = Path("docs/MODULE_BOUNDARIES.md")
BEGIN_MARKER = "<!-- BEGIN AUTO-GENERATED: command-migration-map -->"
END_MARKER = "<!-- END AUTO-GENERATED: command-migration-map -->"


def _command_migration_map() -> list[tuple[str, str]]:
    rows = [("python main.py", "from scrapers import run_wiki_flow; run_wiki_flow()")]
    for module_path, replacement_module_path in get_deprecated_module_migrations():
        rows.append(
            (f"python -m {module_path}", f"python -m {replacement_module_path}"),
        )
    return rows


def build_generated_section() -> str:
    lines: list[str] = []
    lines.append("### 7.2 Canonical command map (CLI/API)")
    lines.append("")
    lines.append(
        "Repo nie utrzymuje już warstwy kompatybilności wstecznej "
        "ani deprecated-wrapperów.",
    )
    lines.append("")
    lines.append("W praktyce oznacza to migrację:")
    lines.append("- z `python -m scrapers.<domain>.list_scraper`")
    lines.append("- na `python -m scrapers.<domain>.entrypoint`")
    lines.append("")
    for module_command, canonical_command in _command_migration_map():
        lines.append(f"- `{module_command}` -> `{canonical_command}`")
    return "\n".join(lines).rstrip() + "\n"


def _replace_between_markers(document: str, generated: str) -> str:
    if BEGIN_MARKER not in document or END_MARKER not in document:
        msg = (
            "Nie znaleziono markerów sekcji auto-generowanej. "
            f"Wymagane markery: {BEGIN_MARKER} / {END_MARKER}."
        )
        raise ValueError(msg)

    before, rest = document.split(BEGIN_MARKER, maxsplit=1)
    _, after = rest.split(END_MARKER, maxsplit=1)

    return f"{before}{BEGIN_MARKER}\n\n{generated}\n{END_MARKER}{after}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generuje sekcję mapy migracji komend do docs/MODULE_BOUNDARIES.md",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Sprawdza czy docs/MODULE_BOUNDARIES.md jest "
            "zsynchronizowany z generatorem."
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Nadpisuje auto-generowaną sekcję w docs/MODULE_BOUNDARIES.md.",
    )
    args = parser.parse_args()

    current = DOC_PATH.read_text(encoding="utf-8")
    generated = build_generated_section()
    updated = _replace_between_markers(current, generated)

    if args.check:
        if current != updated:
            print("docs/MODULE_BOUNDARIES.md jest nieaktualny względem generatora.")
            return 1
        print("docs/MODULE_BOUNDARIES.md jest zsynchronizowany.")
        return 0

    if args.write:
        DOC_PATH.write_text(updated, encoding="utf-8")
        print(f"Zaktualizowano {DOC_PATH}")
        return 0

    print(generated, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
