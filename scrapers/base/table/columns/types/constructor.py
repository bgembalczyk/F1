from scrapers.base.table.columns.types.constructor_base import BaseConstructorColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseConstructorColumn):
    part_parser_cls = ConstructorPartColumn
