"""DOMAIN-SPECIFIC: drivers column rule.

(constructor split) localized for drivers domain.
"""
from scrapers.base.table.columns.types.constructor_base import BaseConstructorColumn
from scrapers.drivers.columns.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseConstructorColumn):
    part_parser_cls = ConstructorPartColumn
