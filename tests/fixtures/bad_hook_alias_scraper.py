class SingleWikiArticleScraperBase: ...


class BadAliasScraper(SingleWikiArticleScraperBase):
    def build_infobox_payload(self, _soup):
        return {}
