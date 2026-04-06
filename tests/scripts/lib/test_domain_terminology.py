from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from scripts.lib.domain_terminology import parse_forbidden_term_map


def test_parse_forbidden_term_map_reads_first_code_block_only(tmp_path: Path) -> None:
    glossary = tmp_path / "DOMAIN_GLOSSARY.md"
    glossary.write_text(
        """
# Header

```
# comment
driver standings -> season standings
constructor standings -> team standings
ignored-without-arrow
```

```
another -> block
```
""",
        encoding="utf-8",
    )

    parsed = parse_forbidden_term_map(glossary)

    assert parsed == {
        "driver standings": "season standings",
        "constructor standings": "team standings",
    }


def test_parse_forbidden_term_map_ignores_blank_or_incomplete_lines(
    tmp_path: Path,
) -> None:
    glossary = tmp_path / "DOMAIN_GLOSSARY.md"
    glossary.write_text(
        """
```
-> canonical
forbidden ->
valid term -> canonical term
```
""",
        encoding="utf-8",
    )

    assert parse_forbidden_term_map(glossary) == {"valid term": "canonical term"}


def test_parse_forbidden_term_map_returns_empty_without_code_block(
    tmp_path: Path,
) -> None:
    glossary = tmp_path / "DOMAIN_GLOSSARY.md"
    glossary.write_text("No code block here\n", encoding="utf-8")

    assert parse_forbidden_term_map(glossary) == {}
