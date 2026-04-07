from pathlib import Path

from scrapers.drivers.helpers import export as export_mod


def test_surname_initial_handles_fallbacks() -> None:
    assert export_mod.surname_initial({"driver": {"text": "Lewis Hamilton"}}) == "H"
    assert export_mod.surname_initial({"driver": {"text": "123"}}) == "other"
    assert export_mod.surname_initial({}) == "other"


def test_export_complete_drivers_uses_grouping_export(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: dict[str, object] = {}

    class _ScraperStub:
        def __init__(self, *, options) -> None:
            self.options = options

        def fetch(self):
            return [
                {"driver": {"text": "Max Verstappen"}},
                {"driver": {"text": "Ayrton Senna"}},
            ]

    class _ExportServiceStub:
        def export_grouped_json(self, scraper, data, output_dir: Path, grouper):
            calls["scraper"] = scraper
            calls["data"] = data
            calls["output_dir"] = output_dir
            calls["group_m"] = grouper(data[0])
            calls["group_a"] = grouper(data[1])

    monkeypatch.setattr(export_mod, "CompleteDriverDataExtractor", _ScraperStub)
    monkeypatch.setattr(export_mod, "ResultExportService", _ExportServiceStub)

    output_dir = tmp_path / "drivers"

    export_mod.export_complete_drivers(
        output_dir=output_dir,
        include_urls=False,
    )

    assert calls["output_dir"] == output_dir
    assert calls["group_m"] == "V"
    assert calls["group_a"] == "S"
