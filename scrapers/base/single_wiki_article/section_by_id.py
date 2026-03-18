from abc import ABC

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase


class SingleWikiArticleSectionByIdBase(
    WikipediaSectionByIdMixin,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant bazy dla scraperów, które używają ``WikipediaSectionByIdMixin``.

    ``fetch_by_url`` pochodzi z mixina i obsługuje URL z fragmentem sekcji.
    """
