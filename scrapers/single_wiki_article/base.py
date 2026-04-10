from scrapers.single_wiki_article.single_article_domain_scraper_base import (
    SingleArticleDomainScraperBase,
)
from infrastructure.helpers import init_scraper_options
from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.helpers.config_factory import build_scraper_options
from scrapers.options import ScraperOptions
from scrapers.wiring.runtime.factory import ScraperRuntimeFactory
from scrapers.section.selection_strategy.base import SectionSelectionStrategy
from scrapers.wiki.scraper_wiki import WikiScraper


class SingleWikiArticleScraperBase(SingleArticleDomainScraperBase):
    """Backward-compatible alias for legacy imports."""


__all__ = ["SingleWikiArticleScraperBase"]
