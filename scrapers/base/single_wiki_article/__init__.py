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
