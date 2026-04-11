from typing import Any

from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.colour import ColourListColumn
from scrapers.columns.types.driver_list import DriverListColumn
from scrapers.columns.types.sponsor import SponsorColumn
from scrapers.columns.types.text import TextColumn
from scrapers.headers_table import normalize_header
from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.table_schema_dsl import TableSchemaDSL


class SponsorshipTableParser(WikiTableHtmlParser):
    @staticmethod
    def build_schema(seasons_col_factory: Any) -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=[
                *SponsorshipTableParser._season_column_specs(seasons_col_factory),
                *SponsorshipTableParser._driver_column_specs(),
                *SponsorshipTableParser._colour_column_specs(),
                *SponsorshipTableParser._sponsor_column_specs(),
                *SponsorshipTableParser._text_column_specs(),
            ],
        )

    @staticmethod
    def _season_column_specs(seasons_col_factory: Any) -> list[Any]:
        return [
            ColumnSpec("Year", "season", seasons_col_factory()),
            ColumnSpec("Years", "season", seasons_col_factory()),
            ColumnSpec("Season", "season", seasons_col_factory()),
            ColumnSpec("Seasons", "season", seasons_col_factory()),
            ColumnSpec("Year(s)", "season", seasons_col_factory()),
        ]

    @staticmethod
    def _driver_column_specs() -> list[Any]:
        return [ColumnSpec("Driver(s)", "drivers", DriverListColumn())]

    @staticmethod
    def _colour_column_specs() -> list[Any]:
        return [
            ColumnSpec(
                "Main colour(s)",
                normalize_header("Main colour(s)"),
                ColourListColumn(),
            ),
            ColumnSpec(
                "Additional colour(s)",
                normalize_header("Additional colour(s)"),
                ColourListColumn(),
            ),
        ]

    @staticmethod
    def _sponsor_column_specs() -> list[Any]:
        return [
            ColumnSpec(
                "Additional major sponsor(s)",
                normalize_header("Additional major sponsor(s)"),
                SponsorColumn(),
            ),
            ColumnSpec(
                "Livery sponsor(s)",
                normalize_header("Livery sponsor(s)"),
                SponsorColumn(),
            ),
            ColumnSpec(
                "Main sponsor(s)",
                normalize_header("Main sponsor(s)"),
                SponsorColumn(),
            ),
            ColumnSpec(
                "Livery principal sponsor(s)",
                "livery_principal_sponsors",
                SponsorColumn(),
            ),
        ]

    @staticmethod
    def _text_column_specs() -> list[Any]:
        return [
            ColumnSpec("Notes", normalize_header("Notes"), TextColumn()),
            ColumnSpec(
                "Non-tobacco liveries",
                normalize_header("Non-tobacco liveries"),
                TextColumn(),
            ),
            ColumnSpec(
                "Special liveries",
                normalize_header("Special liveries"),
                TextColumn(),
            ),
            ColumnSpec(
                "Non-tobacco/alcohol livery changes",
                normalize_header("Non-tobacco/alcohol livery changes"),
                TextColumn(),
            ),
            ColumnSpec(
                "Other Informations (including non-tobacco/alcohol race changes)",
                normalize_header(
                    "Other Informations (including non-tobacco/alcohol race changes)",
                ),
                TextColumn(),
            ),
            ColumnSpec(
                "Other information",
                normalize_header("Other information"),
                TextColumn(),
            ),
            ColumnSpec(
                "Non Tobacco/Alcohol changes(s)",
                normalize_header("Non Tobacco/Alcohol changes(s)"),
                TextColumn(),
            ),
            ColumnSpec(
                "Additional major sponsor(s) / Notes",
                normalize_header("Additional major sponsor(s) / Notes"),
                TextColumn(),
            ),
            ColumnSpec(
                "Location-specific livery changes (2011-present)",
                normalize_header("Location-specific livery changes (2011-present)"),
                TextColumn(),
            ),
            ColumnSpec(
                "Other Changes",
                normalize_header("Other Changes"),
                TextColumn(),
            ),
        ]


__all__ = [
    "SponsorshipTableParser",
]
