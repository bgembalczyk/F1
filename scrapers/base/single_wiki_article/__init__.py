from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
    from scrapers.base.single_wiki_article.dto import InfoboxPayloadDTO
    from scrapers.base.single_wiki_article.dto import SectionsPayloadDTO
    from scrapers.base.single_wiki_article.dto import TablesPayloadDTO
    from scrapers.base.single_wiki_article.section_adapter import (
        SingleWikiArticleSectionAdapterBase,
    )
    from scrapers.base.single_wiki_article.section_by_id import (
        SingleWikiArticleSectionByIdBase,
    )
    from scrapers.base.single_wiki_article.section_selection_strategy import (
        SectionSelectionStrategy,
    )
    from scrapers.base.single_wiki_article.section_selection_strategy import (
        WikipediaSectionByIdSelectionStrategy,
    )

__all__ = [
    "InfoboxPayloadDTO",
    "SectionsPayloadDTO",
    "SingleWikiArticleScraperBase",
    "SingleWikiArticleSectionAdapterBase",
    "SingleWikiArticleSectionByIdBase",
    "TablesPayloadDTO",
    "SectionSelectionStrategy",
    "WikipediaSectionByIdSelectionStrategy",
]


def __getattr__(name: str) -> Any:
    if name == "SingleWikiArticleScraperBase":
        from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase

        return SingleWikiArticleScraperBase
    if name in {"InfoboxPayloadDTO", "SectionsPayloadDTO", "TablesPayloadDTO"}:
        from scrapers.base.single_wiki_article.dto import InfoboxPayloadDTO
        from scrapers.base.single_wiki_article.dto import SectionsPayloadDTO
        from scrapers.base.single_wiki_article.dto import TablesPayloadDTO

        return {
            "InfoboxPayloadDTO": InfoboxPayloadDTO,
            "SectionsPayloadDTO": SectionsPayloadDTO,
            "TablesPayloadDTO": TablesPayloadDTO,
        }[name]
    if name == "SingleWikiArticleSectionAdapterBase":
        from scrapers.base.single_wiki_article.section_adapter import (
            SingleWikiArticleSectionAdapterBase,
        )

        return SingleWikiArticleSectionAdapterBase
    if name == "SingleWikiArticleSectionByIdBase":
        from scrapers.base.single_wiki_article.section_by_id import (
            SingleWikiArticleSectionByIdBase,
        )

        return SingleWikiArticleSectionByIdBase
    if name in {"SectionSelectionStrategy", "WikipediaSectionByIdSelectionStrategy"}:
        from scrapers.base.single_wiki_article.section_selection_strategy import (
            SectionSelectionStrategy,
        )
        from scrapers.base.single_wiki_article.section_selection_strategy import (
            WikipediaSectionByIdSelectionStrategy,
        )

        return {
            "SectionSelectionStrategy": SectionSelectionStrategy,
            "WikipediaSectionByIdSelectionStrategy": WikipediaSectionByIdSelectionStrategy,
        }[name]
    raise AttributeError(name)
