from __future__ import annotations

from pathlib import Path

from scripts.check_single_wiki_hook_names import lint_path
from scripts.check_single_wiki_hook_names import main


def test_linter_accepts_standard_hooks(tmp_path: Path) -> None:
    file_path = tmp_path / "good_scraper.py"
    file_path.write_text(
        """
class GoodScraper(SingleWikiArticleScraperBase):
    def _build_infobox_payload(self, soup):
        return {}

    def _build_tables_payload(self, soup):
        return {}

    def _build_sections_payload(self, soup):
        return {}

    def _assemble_record(self, **kwargs):
        return {}
""".strip(),
        encoding="utf-8",
    )

    assert lint_path(file_path) == []


def test_linter_rejects_non_standard_alias() -> None:
    file_path = Path("tests/fixtures/bad_hook_alias_scraper.py")

    errors = lint_path(file_path)

    assert errors
    assert "build_infobox_payload" in errors[0]


def test_linter_allows_alias_with_justification(tmp_path: Path) -> None:
    file_path = tmp_path / "allowed_alias_scraper.py"
    file_path.write_text(
        """
class AllowedAliasScraper(SingleWikiArticleScraperBase):
    # hook-name-allow: migration compatibility
    def build_infobox_payload(self, soup):
        return {}
""".strip(),
        encoding="utf-8",
    )

    assert lint_path(file_path) == []


def test_cli_supports_explicit_empty_target_list(capsys) -> None:
    exit_code = main(["--paths"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[single-wiki-hook-names] OK" in captured.out


def test_cli_supports_explicit_target_list(tmp_path: Path, capsys) -> None:
    bad_file = tmp_path / "bad_scraper.py"
    bad_file.write_text(
        """
class BadScraper(SingleWikiArticleScraperBase):
    def build_infobox_payload(self, soup):
        return {}
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(["--paths", str(bad_file)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "[single-wiki-hook-names] ERROR" in captured.out
    assert "unsupported hook alias 'build_infobox_payload'" in captured.out
