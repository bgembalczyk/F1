from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scrapers.cli import MODULE_DEFINITIONS

DOC_PATH = Path("docs/MODULE_BOUNDARIES.md")
BEGIN_MARKER = "<!-- BEGIN AUTO-GENERATED: command-migration-map -->"
END_MARKER = "<!-- END AUTO-GENERATED: command-migration-map -->"


def _legacy_list_entrypoints() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for definition in MODULE_DEFINITIONS.values():
        if not definition.deprecated:
            continue
        replacement = definition.replacement_module_path
        if replacement is None:
            continue
        pairs.append((definition.module_path, replacement))
    return sorted(pairs)


def _other_legacy_modules() -> list[str]:
    modules = [
        definition.module_path
        for definition in MODULE_DEFINITIONS.values()
        if definition.deprecated and definition.replacement_module_path is None
    ]
    return sorted(modules)


def _command_migration_map() -> list[tuple[str, str]]:
    rows = [
        (
            "python main.py --mode <layer0|layer1|full>",
            "python -m scrapers.cli wiki --mode <layer0|layer1|full>",
        )
    ]
    for module_path in sorted(MODULE_DEFINITIONS):
        rows.append(
            (
                f"python -m {module_path}",
                f"python -m scrapers.cli run {module_path}",
            )
        )
    return rows


def build_generated_section() -> str:
    lines: list[str] = []
    lines.append("### 7.2 Deprecated moduły i zamienniki (CLI/API)")
    lines.append("")
    lines.append("#### Domenowe list-entrypointy (preferowane nowe API)")
    lines.append("")
    for legacy_module, replacement_module in _legacy_list_entrypoints():
        lines.append(f"- `{legacy_module}` -> `{replacement_module}`")
    lines.append("")
    lines.append("W praktyce oznacza to migrację:")
    lines.append("- z `python -m scrapers.cli run scrapers.<domain>.list_scraper`")
    lines.append("- na `python -m scrapers.cli run scrapers.<domain>.entrypoint`")
    lines.append("")
    lines.append(
        "#### Pozostałe legacy moduły (bez nowego modułu API, canonical przez `scrapers.cli run`)"
    )
    lines.append("")
    for module in _other_legacy_modules():
        lines.append(f"- `{module}`")
    lines.append("")
    lines.append("### Mapa `old_command -> new_command`")
    lines.append("")
    for old_command, new_command in _command_migration_map():
        lines.append(f"- `{old_command}` -> `{new_command}`")
    lines.append("")
    lines.append(
        "Każdy wrapper legacy emituje `DeprecationWarning` z powyższym mapowaniem."
    )
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
        description="Generuje sekcję mapy migracji komend do docs/MODULE_BOUNDARIES.md"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Sprawdza czy docs/MODULE_BOUNDARIES.md jest zsynchronizowany z generatorem.",
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
