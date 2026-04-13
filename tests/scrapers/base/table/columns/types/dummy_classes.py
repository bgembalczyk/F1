from scrapers.columns.types.constructor.base import BaseConstructorColumn
from scrapers.columns.types.constructor.part import ConstructorPartColumn


class ContractConstructorColumn(BaseConstructorColumn):
    part_parser_cls = ConstructorPartColumn


