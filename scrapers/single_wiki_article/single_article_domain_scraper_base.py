from __future__ import annotations

from abc import ABC

from scrapers.single_wiki_article.single_article_domain_pipeline_base import (
    SingleArticleDomainPipelineBase,
)


class SingleArticleDomainScraperBase(
    SingleArticleDomainPipelineBase,
    ABC,
):
    """Backward-compatible alias of the extracted domain pipeline base."""


__all__ = ["SingleArticleDomainScraperBase"]
