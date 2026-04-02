from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map


def test_build_layer_zero_run_config_factory_map_contains_parser_scopes() -> None:
    factories = build_layer_zero_run_config_factory_map()

    expected = {
        "constructors_current": {"export_scope": "current"},
        "constructors_former": {"export_scope": "former"},
        "constructors_indianapolis_only": {"export_scope": "indianapolis"},
        "constructors_privateer": {"export_scope": "privateer"},
        "engines_indianapolis_only": {"export_scope": "indianapolis_only"},
        "points_history": {"export_scope": "history"},
        "points_shortened": {"export_scope": "shortened"},
        "points_sprint": {"export_scope": "sprint"},
        "grands_prix_red_flagged_world_championship": {
            "export_scope": "world_championship"
        },
        "grands_prix_red_flagged_non_championship": {
            "export_scope": "non_championship"
        },
    }

    for seed_name, kwargs in expected.items():
        factory = factories[seed_name]
        assert factory.create_scraper_kwargs(job=None) == kwargs
