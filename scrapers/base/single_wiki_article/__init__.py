from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "InfoboxPayloadDTO",
    "SectionSelectionStrategy",
    "SectionsPayloadDTO",
    "SingleWikiArticleScraperBase",
    "SingleWikiArticleSectionAdapterBase",
    "SingleWikiArticleSectionByIdBase",
    "TablesPayloadDTO",
    "WikipediaSectionByIdSelectionStrategy",
]

_EXPORT_MAP: dict[str, tuple[str, str]] = {
    "InfoboxPayloadDTO": ("scrapers.base.single_wiki_article.dto", "InfoboxPayloadDTO"),
    "SectionSelectionStrategy": (
        "scrapers.base.single_wiki_article.section_selection_strategy",
        "SectionSelectionStrategy",
    ),
    "SectionsPayloadDTO": (
        "scrapers.base.single_wiki_article.dto",
        "SectionsPayloadDTO",
    ),
    "SingleWikiArticleScraperBase": (
        "scrapers.base.single_wiki_article.base",
        "SingleWikiArticleScraperBase",
    ),
    "SingleWikiArticleSectionAdapterBase": (
        "scrapers.base.single_wiki_article.section_adapter",
        "SingleWikiArticleSectionAdapterBase",
    ),
    "SingleWikiArticleSectionByIdBase": (
        "scrapers.base.single_wiki_article.section_by_id",
        "SingleWikiArticleSectionByIdBase",
    ),
    "TablesPayloadDTO": (
        "scrapers.base.single_wiki_article.dto",
        "TablesPayloadDTO",
    ),
    "WikipediaSectionByIdSelectionStrategy": (
        "scrapers.base.single_wiki_article.section_selection_strategy",
        "WikipediaSectionByIdSelectionStrategy",
    ),
}


def __getattr__(name: str) -> Any:
    module_and_attr = _EXPORT_MAP.get(name)
    if module_and_attr is None:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    module_name, attr_name = module_and_attr
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
