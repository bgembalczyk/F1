from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article.section_adapter import (
    SingleWikiArticleSectionAdapterBase,
)
from scrapers.base.single_wiki_article.section_by_id import (
    SingleWikiArticleSectionByIdBase,
)
from scrapers.base.single_wiki_article.strategies import SectionSelectionStrategy
from scrapers.base.single_wiki_article.strategies import UrlFragmentStrategy

__all__ = [
    "SingleWikiArticleScraperBase",
    "SingleWikiArticleSectionAdapterBase",
    "SingleWikiArticleSectionByIdBase",
    "SectionSelectionStrategy",
    "UrlFragmentStrategy",
]
