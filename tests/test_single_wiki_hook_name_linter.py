from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_single_wiki_hook_names import lint_path
from tests.support.single_wiki_hook_linter_helpers import (
    build_scraper_source,
    write_and_lint,
)


def test_linter_accepts_standard_hooks(tmp_path: Path) -> None:
    source = build_scraper_source(
        class_name="GoodScraper",
        methods=[
            "_build_infobox_payload",
            "_build_tables_payload",
            "_build_sections_payload",
            "_assemble_record",
        ],
    )

    assert write_and_lint(tmp_path=tmp_path, source=source, filename="good_scraper.py") == []


def test_linter_rejects_non_standard_alias() -> None:
    file_path = Path("tests/fixtures/bad_hook_alias_scraper.py")

    errors = lint_path(file_path)

    assert errors
    assert "build_infobox_payload" in errors[0]


@pytest.mark.parametrize(
    ("alias_method_name", "expected_fragment"),
    [
        ("build_infobox_payload", "build_infobox_payload"),
        ("legacy_build_tables_payload", "legacy_build_tables_payload"),
        ("custom_build_sections_payload", "custom_build_sections_payload"),
        ("pre_assemble_record", "pre_assemble_record"),
    ],
)
def test_linter_rejects_multiple_aliases_in_table(
    tmp_path: Path,
    alias_method_name: str,
    expected_fragment: str,
) -> None:
    source = build_scraper_source(
        class_name="AliasScraper",
        methods=[alias_method_name],
    )

    errors = write_and_lint(
        tmp_path=tmp_path,
        source=source,
        filename=f"alias_{alias_method_name}.py",
    )

    assert errors
    assert expected_fragment in errors[0]


def test_linter_allows_alias_with_justification(tmp_path: Path) -> None:
    source = build_scraper_source(
        class_name="AllowedAliasScraper",
        methods=["build_infobox_payload"],
        header_comments=["# hook-name-allow: migration compatibility"],
    )

    assert write_and_lint(
        tmp_path=tmp_path,
        source=source,
        filename="allowed_alias_scraper.py",
    ) == []
