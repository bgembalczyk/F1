import json
import re

import pytest
from bs4 import BeautifulSoup

from scrapers.debug_dumps import TablePipelineDebugContext
from scrapers.debug_dumps import write_infobox_dump
from scrapers.debug_dumps import write_table_pipeline_dump
from scrapers.infobox.extraction.extractor import BaseInfoboxExtractor
from tests.scrapers.base.dummy_classes import FailingParser
from tests.scrapers.base.dummy_classes import PassThroughMapper


def test_debug_enabled_generates_infobox_dump_on_extract_failure(tmp_path) -> None:
    soup = BeautifulSoup(
        '<table class="infobox"><tr><th>Name</th><td>Test</td></tr></table>',
        "html.parser",
    )
    extractor = BaseInfoboxExtractor(
        parser=FailingParser(),
        mapper=PassThroughMapper(),
        debug_dir=tmp_path,
        run_id="run-123",
        url="https://example.com/wiki/Test",
    )

    with pytest.raises(ValueError, match="boom"):
        extractor.extract(soup)

    dumps = list(tmp_path.glob("infobox_run-123_*.html"))
    assert len(dumps) == 1
    assert "<table" in dumps[0].read_text(encoding="utf-8")


def test_debug_disabled_does_not_generate_infobox_dump_on_extract_failure(
    tmp_path,
) -> None:
    soup = BeautifulSoup(
        '<table class="infobox"><tr><th>Name</th><td>Test</td></tr></table>',
        "html.parser",
    )
    extractor = BaseInfoboxExtractor(
        parser=FailingParser(),
        mapper=PassThroughMapper(),
        debug_dir=None,
    )

    with pytest.raises(ValueError, match="boom"):
        extractor.extract(soup)

    assert list(tmp_path.iterdir()) == []


def test_dump_file_naming_for_infobox_and_table_pipeline(tmp_path) -> None:
    infobox_dump = write_infobox_dump(
        tmp_path,
        html="<table></table>",
        url="https://example.com",
        run_id="abc",
    )
    assert re.match(r"^infobox_abc_\d{8}T\d{6}Z\.html$", infobox_dump.name)

    context = TablePipelineDebugContext(
        url="https://example.com",
        section_id="history",
        header="Year",
        row_index=3,
        run_id="run-1",
    )
    table_dump = write_table_pipeline_dump(
        tmp_path,
        context=context,
        cell_html="<td>1950</td>",
        error=RuntimeError("parse error"),
    )
    assert re.match(
        r"^table_pipeline_\d{8}T\d{6}Z_[0-9a-f]{32}\.json$",
        table_dump.name,
    )

    payload = json.loads(table_dump.read_text(encoding="utf-8"))
    assert payload["context"]["section_id"] == "history"
    assert payload["error"] == {"type": "RuntimeError", "message": "parse error"}
