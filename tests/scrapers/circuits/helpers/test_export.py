from pathlib import Path

from scrapers.circuits.circuits_helpers import export as export_mod


def test_circuit_name_initial_handles_missing_and_text() -> None:
    assert export_mod.circuit_name_initial({"name": {"list": ["Monza Circuit"]}}) == "M"
    assert export_mod.circuit_name_initial({"name": {"list": [""]}}) == "other"
    assert export_mod.circuit_name_initial({}) == "other"


def test_export_complete_circuits_groups_records_and_exports(
    monkeypatch,
    tmp_path,
) -> None:
    exported_paths: list[Path] = []

    class _Logger:
        def info(self, *_args, **_kwargs):
            return None

    class _Exporter:
        pass

    class _ScraperStub:
        url = "https://example.com/circuits"
        logger = _Logger()
        exporter = _Exporter()

        def __init__(self, *, options) -> None:
            self.options = options

        def fetch(self):
            return [
                {"name": {"list": ["Monza"]}},
                {"name": {"list": ["Austin"]}},
                {"name": {"list": [""]}},
            ]

    class _ExportServiceStub:
        def to_json(self, result, path: Path, exporter=None):
            _ = result, exporter
            exported_paths.append(path)

        def export_grouped_json(self, _scraper, data, output_dir, key_fn):
            from collections import defaultdict

            grouped = defaultdict(list)
            for record in data:
                grouped[key_fn(record)].append(record)
            exported_paths.extend([output_dir / f"{key}.json" for key in grouped])

    monkeypatch.setattr(export_mod, "F1CompleteCircuitDataExtractor", _ScraperStub)
    monkeypatch.setattr(export_mod, "ResultExportService", _ExportServiceStub)

    export_mod.export_complete_circuits(output_dir=tmp_path)

    names = sorted(path.name for path in exported_paths)
    assert names == ["A.json", "M.json", "other.json"]
