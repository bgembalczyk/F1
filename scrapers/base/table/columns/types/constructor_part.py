import re

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.helpers import extract_constructor_part
from scrapers.base.table.columns.types.func import FuncColumn


class ConstructorPartColumn(FuncColumn):
    def __init__(self, index: int) -> None:
        super().__init__(lambda ctx: extract_constructor_part(ctx, index))




