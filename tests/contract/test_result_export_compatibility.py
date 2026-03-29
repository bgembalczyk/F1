import json

from scrapers.base.results import ScrapeResult
from scrapers.base.services.result_export_service import ResultExportService


def test_json_export_contract_is_backward_compatible(tmp_path) -> None:
    result = ScrapeResult(
        data=[{"driver": "Lewis"}, {"driver": "Max"}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.json"

    ResultExportService().to_json(result, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload == [{"driver": "Lewis"}, {"driver": "Max"}]


def test_csv_export_contract_is_backward_compatible(tmp_path) -> None:
    result = ScrapeResult(
        data=[{"b": 1, "a": 2}, {"c": 3, "b": 4}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.csv"

    ResultExportService().to_csv(result, output, include_metadata=True)

    content = output.read_text(encoding="utf-8").splitlines()
    metadata = json.loads(content[0].replace("# meta: ", ""))

    assert metadata["source_url"] == "https://example.com"
    assert metadata["records_count"] == 2
    assert content[1] == "b,a,c"
    assert content[2] == "1,2,"
    assert content[3] == "4,,3"
