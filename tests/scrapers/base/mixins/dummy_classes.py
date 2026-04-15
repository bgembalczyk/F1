from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class StubApplyForElements(RecursiveSectionParser):
    def __init__(self, table_parser):
        super().__init__()
        self._table_parser = table_parser
