from __future__ import annotations


from scripts.check_single_wiki_hook_names import lint_path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def build_scraper_source(
    *,
    class_name: str = "TestScraper",
    methods: list[str],
    base_class: str = "SingleWikiArticleScraperBase",
    header_comments: list[str] | None = None,
) -> str:
    """Build a minimal scraper source for single-wiki hook linter tests."""

    comments_block = ""
    if header_comments:
        comments_block = "\n".join(header_comments) + "\n"

    indented_methods = "\n\n".join(
        f"    def {method}(self, soup):\n        return {{}}" for method in methods
    )

    return f"{comments_block}class {class_name}({base_class}):\n{indented_methods}\n"


def write_and_lint(
    *,
    tmp_path: Path,
    source: str,
    filename: str = "scraper.py",
) -> list[str]:
    file_path = tmp_path / filename
    file_path.write_text(source, encoding="utf-8")
    return lint_path(file_path)
