from scrapers.mixins.apply_for_elements import ApplyForElementsMixin


class StubApplyForElements(ApplyForElementsMixin):
    def __init__(self, table_parser):
        self._table_parser = table_parser


