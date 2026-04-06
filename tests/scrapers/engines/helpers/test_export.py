from pathlib import Path

from scrapers.engines.helpers import export as export_mod


def test_manufacturer_name_initial_handles_text_dict_and_fallback() -> None:
    assert (
        export_mod.manufacturer_name_initial(
            {"manufacturer": {"text": "Honda"}},
        )
        == "H"
    )
    assert export_mod.manufacturer_name_initial({"manufacturer": "Renault"}) == "R"
    assert export_mod.manufacturer_name_initial({"manufacturer": "123"}) == "other"


def test_export_complete_engine_manufacturers_groups_output(
    monkeypatch,
    tmp_path,
) -> None:
    exported: list[Path] = []

    class _Logger:
        def info(self, *_args, **_kwargs):
            return None

    class _Exporter:
        pass

    class _ScraperStub:
        logger = _Logger()
        exporter = _Exporter()
        url = "https://example.com/engines"

        def __init__(self, *, options):
            self.options = options

        def fetch(self):
            return [
                {"manufacturer": {"text": "Honda"}},
                {"manufacturer": "BMW"},
                {"manufacturer": ""},
            ]

    class _ExportServiceStub:
        def to_json(self, result, path: Path, exporter=None):
            _ = result, exporter
            exported.append(path)

    monkeypatch.setattr(
        export_mod,
        "F1CompleteEngineManufacturerDataExtractor",
        _ScraperStub,
    )
    monkeypatch.setattr(export_mod, "ResultExportService", _ExportServiceStub)

    export_mod.export_complete_engine_manufacturers(output_dir=tmp_path)

    assert sorted(path.name for path in exported) == ["B.json", "H.json", "other.json"]
