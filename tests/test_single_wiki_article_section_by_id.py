import pytest
from scrapers.base.single_wiki_article.section_by_id import SingleWikiArticleSectionByIdBase
from scrapers.base.single_wiki_article.section_selection_strategy import WikipediaSectionByIdSelectionStrategy

class ConcreteScraper(SingleWikiArticleSectionByIdBase):
    def _assemble_record(self, *args, **kwargs):
        pass

def test_single_wiki_article_section_by_id_init():
    scraper = ConcreteScraper()
    assert isinstance(scraper.section_selection_strategy, WikipediaSectionByIdSelectionStrategy)

def test_single_wiki_article_section_by_id_custom_strategy():
    class CustomStrategy:
        pass

    strategy = CustomStrategy()
    scraper = ConcreteScraper(section_selection_strategy=strategy)
    assert scraper.section_selection_strategy is strategy
