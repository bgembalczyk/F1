from pathlib import Path

from scrapers.drivers.helpers import export as export_mod


def test_surname_initial_handles_fallbacks() -> None:
    assert export_mod.surname_initial({"driver": {"text": "Lewis Hamilton"}}) == "H"
    assert export_mod.surname_initial({"driver": {"text": "123"}}) == "other"
    assert export_mod.surname_initial({}) == "other"


def test_export_complete_drivers_uses_grouping_export(monkeypatch) -> None:
    calls: dict[str, object] = {}

    class _ScraperStub:
        def __init__(self, *, options) -> None:
            self.options = options

        def fetch(self):
            return [
                {"driver": {"text": "Max Verstappen"}},
                {"driver": {"text": "Ayrton Senna"}},
            ]

    def _fake_export(scraper, data, output_dir: Path, grouper):
        calls["scraper"] = scraper
        calls["data"] = data
        calls["output_dir"] = output_dir
        calls["group_m"] = grouper(data[0])
        calls["group_a"] = grouper(data[1])

    monkeypatch.setattr(export_mod, "CompleteDriverDataExtractor", _ScraperStub)
    monkeypatch.setattr(export_mod, "export_grouped_json", _fake_export)

    export_mod.export_complete_drivers(
        output_dir=Path("/tmp/drivers"),
        include_urls=False,
    )

    assert calls["output_dir"] == Path("/tmp/drivers")
    assert calls["group_m"] == "V"
    assert calls["group_a"] == "S"
