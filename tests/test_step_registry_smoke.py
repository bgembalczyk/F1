from __future__ import annotations

from pipeline import step_registry


def test_registry_exposes_layered_steps():
    layer0 = step_registry.get_layer0_steps()
    layer1 = step_registry.get_layer1_steps()

    assert layer0
    assert layer1
    assert layer0[0].step_id.startswith("layer0_")
    assert layer1[0].step_id.startswith("layer1_")


def test_layer0_runner_uses_mocked_run_and_export(monkeypatch):
    calls = []

    class DummyScraper:
        __name__ = "DummyScraper"

    def fake_load_attr(_module_path, attr_name):
        if attr_name == "CircuitsListScraper":
            return DummyScraper
        message = "Unexpected attr"
        raise AssertionError(message)

    def fake_run_and_export(scraper_cls, json_rel, csv_rel=None):
        calls.append((scraper_cls.__name__, json_rel, csv_rel))

    monkeypatch.setattr(step_registry, "_load_attr", fake_load_attr)
    monkeypatch.setattr(step_registry, "_run_and_export", fake_run_and_export)

    step = step_registry.get_layer0_steps()[0]
    step.run()

    assert calls == [("DummyScraper", "circuits/f1_circuits.json", None)]


def test_layer1_runner_uses_mocked_exporter(monkeypatch):
    calls = []

    def fake_export_complete_circuits(*, output_dir, include_urls):
        calls.append((output_dir, include_urls))

    def fake_load_attr(_module_path, attr_name):
        if attr_name == "export_complete_circuits":
            return fake_export_complete_circuits
        if attr_name == "F1CompleteGrandPrixDataExtractor":
            class DummyScraper:
                __name__ = "DummyGrandPrix"

            return DummyScraper
        message = "Unexpected attr"
        raise AssertionError(message)

    def fake_run_and_export(_scraper_cls, _json_rel, _csv_rel=None):
        return None

    monkeypatch.setattr(step_registry, "_load_attr", fake_load_attr)
    monkeypatch.setattr(step_registry, "_run_and_export", fake_run_and_export)

    circuits_step = next(
        step
        for step in step_registry.get_layer1_steps()
        if step.step_id == "layer1_complete_circuits"
    )
    circuits_step.run()

    assert calls
    assert str(calls[0][0]).endswith("circuits/complete_circuits")
    assert calls[0][1] is True
