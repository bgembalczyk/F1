"""DOMAIN-SPECIFIC: constructors constructor parser with local part parser."""

from scrapers.base.table.columns.types.constructor_base import BaseConstructorColumn
from scrapers.constructors.columns.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseConstructorColumn):
    part_parser_cls = ConstructorPartColumn
