from __future__ import annotations

from pathlib import Path

GLOSSARY_PATH = Path("docs/DOMAIN_GLOSSARY.md")


def parse_forbidden_term_map(glossary_path: Path) -> dict[str, str]:
    """Parse forbidden term mappings from glossary text code block.

    Expected format per line: `forbidden -> canonical`.
    """
    content = glossary_path.read_text(encoding="utf-8")
    in_block = False
    mapping: dict[str, str] = {}

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("```") and not in_block:
            in_block = True
            continue
        if line.startswith("```") and in_block:
            break
        if not in_block or not line or line.startswith("#"):
            continue

        if "->" not in line:
            continue
        forbidden, canonical = [item.strip() for item in line.split("->", 1)]
        if forbidden and canonical:
            mapping[forbidden] = canonical

    return mapping
