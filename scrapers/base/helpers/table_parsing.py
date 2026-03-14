"""Shared utility for parsing HTML tables with pipeline."""

from typing import Any

from bs4 import Tag

from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline


class TableParsingHelper:
    """Helper class for parsing HTML tables with pipeline."""

    @staticmethod
    def parse_table_with_pipeline(
        table: Tag,
        pipeline: TablePipeline,
    ) -> list[dict[str, Any]]:
        """Parse a table using the provided pipeline.

        Args:
            table: BeautifulSoup Tag representing the table
            pipeline: TablePipeline to use for parsing

        Returns:
            List of parsed records
        """
        parser = HtmlTableParser()
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse_table(table)):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                records.append(record)
        return records
