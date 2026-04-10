from __future__ import annotations

import warnings

from scrapers.single_wiki_article.single_article_domain_pipeline_base import (
    SingleArticleDomainPipelineBase,
)

warnings.warn(
    "scrapers.single_wiki_article.base.SingleWikiArticleScraperBase is deprecated; "
    "use scrapers.single_wiki_article.single_article_domain_pipeline_base."
    "SingleArticleDomainPipelineBase instead.",
    DeprecationWarning,
    stacklevel=2,
)

SingleWikiArticleScraperBase = SingleArticleDomainPipelineBase

__all__ = ["SingleWikiArticleScraperBase"]
