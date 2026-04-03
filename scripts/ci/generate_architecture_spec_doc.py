#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.architecture_spec import ARCHITECTURE_SPEC  # noqa: E402

DEFAULT_OUTPUT = Path("docs/architecture/ARCHITECTURE_SPEC.md")


def _render_layout_section() -> str:
    lines: list[str] = [
        "## layout",
        "",
        "### Domains",
        "",
        "| Domain | Entrypoint | Layers |",
        "|---|---|---|",
    ]
    for domain in ARCHITECTURE_SPEC.domains:
        entrypoint = "yes" if domain.has_entrypoint else "no"
        layers = ", ".join(domain.required_layers) if domain.required_layers else "-"
        lines.append(f"| `{domain.name}` | {entrypoint} | {layers} |")

    lines.extend(
        [
            "",
            "### Shared layers",
            "",
            ", ".join(f"`{layer}`" for layer in ARCHITECTURE_SPEC.layers),
        ],
    )
    return "\n".join(lines)


def _render_rules_section() -> str:
    lines: list[str] = ["## rules", "", "### Forbidden imports by layer", ""]
    for layer in ARCHITECTURE_SPEC.layers:
        forbidden = ARCHITECTURE_SPEC.forbidden_imports_by_layer[layer]
        items = ", ".join(f"`{item}`" for item in forbidden)
        lines.append(f"- `{layer}` cannot import: {items}")

    lines.extend(["", "### Allowed imports by layer", ""])
    for layer in ARCHITECTURE_SPEC.layers:
        allowed = ARCHITECTURE_SPEC.allowed_imports_by_layer[layer]
        items = ", ".join(f"`{item}`" for item in allowed) if allowed else "-"
        lines.append(f"- `{layer}` may import: {items}")

    return "\n".join(lines)


def _render_deprecation_map_section() -> str:
    lines: list[str] = [
        "## deprecation map",
        "",
        "### Lifecycle",
        "",
        "| Stage | Description |",
        "|---|---|",
    ]
    for stage in ARCHITECTURE_SPEC.legacy_lifecycle:
        lines.append(f"| `{stage.stage}` | {stage.description} |")

    lines.extend(
        [
            "",
            "### Legacy module migration",
            "",
            "| Old module/command | New module/command | Notes |",
            "|---|---|---|",
        ],
    )
    for mapping in ARCHITECTURE_SPEC.legacy_module_mappings:
        notes = mapping.notes or "-"
        lines.append(f"| `{mapping.old_module}` | `{mapping.new_module}` | {notes} |")

    return "\n".join(lines)


def render_markdown() -> str:
    sections = [
        "# Architecture Spec",
        "",
        "Generated from `scripts/ci/architecture_spec.py`. Do not edit manually.",
        "",
        _render_layout_section(),
        "",
        _render_rules_section(),
        "",
        _render_deprecation_map_section(),
        "",
    ]
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate architecture spec markdown from code spec.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render_markdown()
    if args.check:
        existing = (
            args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        )
        if existing != rendered:
            print(
                f"Architecture spec doc is out of date: {args.output}. "
                "Run scripts/ci/generate_architecture_spec_doc.py to regenerate.",
            )
            return 1
        print(f"Architecture spec doc is up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
