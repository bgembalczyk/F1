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
    "SingleWikiArticleScraperBase",
    "InfoboxPayloadDTO",
    "TablesPayloadDTO",
    "SectionsPayloadDTO",
    "SingleWikiArticleSectionAdapterBase",
    "SingleWikiArticleSectionByIdBase",
    "WikipediaSectionByIdSelectionStrategy",
    "SectionSelectionStrategy",
]
