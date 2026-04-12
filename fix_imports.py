import re
import os
from pathlib import Path

# Comprehensive mapping: (old_module, new_module)
MAPPINGS = [
    # scrapers.base.* → scrapers.*
    ("scrapers.base.abc", "scrapers.abc"),
    ("scrapers.base.errors_report", "scrapers.errors_report"),
    ("scrapers.base.errors", "scrapers.errors"),
    ("scrapers.base.results", "scrapers.results"),
    ("scrapers.base.cache_adapter", "scrapers.cache_adapter"),
    ("scrapers.base.composite_scraper", "scrapers.composite_scraper"),
    ("scrapers.base.constants.naming", "scrapers.constants.naming"),
    ("scrapers.base.data_extractor", "scrapers.data_extractor"),
    ("scrapers.base.debug_dumps", "scrapers.debug_dumps"),
    ("scrapers.base.domain_entrypoint", "scrapers.domain_entrypoint"),
    ("scrapers.base.error_handler", "scrapers.error_handler"),
    ("scrapers.base.exporters.protocol", "exporters.protocol"),
    ("scrapers.base.exporters.data", "exporters.data"),
    ("scrapers.base.exporters.service", "exporters.service"),
    ("scrapers.base.exporters", "exporters"),
    ("scrapers.base.extractors.table", "scrapers.extractors.table"),
    ("scrapers.base.factory.factory", "scrapers.wiring.factory"),
    ("scrapers.base.factory.run_config_options_mapper", "scrapers.run_config_options_mapper"),
    ("scrapers.base.formatters.csv", "scrapers.formatters.csv"),
    ("scrapers.base.formatters.json", "scrapers.formatters.json"),
    ("scrapers.base.formatters.pandas", "scrapers.formatters.pandas"),
    ("scrapers.base.helpers.config_factory", "scrapers.helpers.config_factory"),
    ("scrapers.base.helpers.date_parsing", "scrapers.helpers.date_parsing"),
    ("scrapers.base.helpers.helpers", "infrastructure.helpers"),
    ("scrapers.base.helpers.html_utils", "scrapers.helpers.html_utils"),
    ("scrapers.base.helpers.links", "scrapers.helpers.links"),
    ("scrapers.base.helpers.normalize", "scrapers.helpers.normalize"),
    ("scrapers.base.helpers.parsing", "scrapers.helpers.parsing"),
    ("scrapers.base.helpers.sections", "scrapers.helpers.sections"),
    ("scrapers.base.helpers.tables.lap_records_table", "scrapers.lap_records_table"),
    ("scrapers.base.helpers.text_normalization", "scrapers.helpers.text_normalization"),
    ("scrapers.base.helpers.time", "scrapers.helpers.time"),
    ("scrapers.base.helpers.transform_micro_ops", "scrapers.helpers.transform_micro_ops"),
    ("scrapers.base.helpers.transformer_utils", "scrapers.helpers.transformer_utils"),
    ("scrapers.base.helpers.transformers", "scrapers.helpers.transformers"),
    ("scrapers.base.helpers.url", "scrapers.helpers.url"),
    ("scrapers.base.helpers.value_objects.normalized_time", "models.value_objects.normalized_time"),
    ("scrapers.base.helpers.value_objects.lap_record", "models.value_objects.lap_record"),
    ("scrapers.base.helpers.wiki", "scrapers.helpers.wiki"),
    ("scrapers.base.helpers.year_extractor", "scrapers.year_extractor"),
    ("scrapers.base.html_fetcher", "scrapers.html_fetcher"),
    ("scrapers.base.infobox.field_mapper", "scrapers.infobox.field.mapper"),
    ("scrapers.base.infobox.html_parser", "scrapers.infobox.wikipedia"),
    ("scrapers.base.infobox.schema", "scrapers.infobox.schemas.schema"),
    ("scrapers.base.infobox.scraper", "scrapers.infobox.extraction.base"),
    ("scrapers.base.list.indianapolis_only_scraper", "scrapers.list.indianapolis_only.base"),
    ("scrapers.base.list.scraper", "scrapers.list.base"),
    ("scrapers.base.logging", "scrapers.logging"),
    ("scrapers.base.mappers.infobox_record", "scrapers.records.mappers.infobox"),
    ("scrapers.base.mappers.section_record", "scrapers.records.mappers.section"),
    ("scrapers.base.mappers.table_record", "scrapers.records.mappers.table_record"),
    ("scrapers.base.mixins.apply_for_elements", "scrapers.mixins.apply_for_elements"),
    ("scrapers.base.mixins.section_table_parse", "scrapers.mixins.section_table_parse"),
    ("scrapers.base.normalization_pipeline", "scrapers.normalization_pipeline"),
    ("scrapers.base.normalization", "scrapers.normalization"),
    ("scrapers.base.pipeline_runner", "scrapers.runners.pipeline_runner"),
    ("scrapers.base.sections.adapter", "scrapers.adapters.section.adapter"),
    ("scrapers.base.sections.constants", "scrapers.section.constants"),
    ("scrapers.base.sections.contract_validation", "scrapers.section.contract_validation"),
    ("scrapers.base.services.result_export_service", "scrapers.services.result_export"),
    ("scrapers.base.single_wiki_article", "scrapers.single_wiki_article"),
    ("scrapers.base.table.columns.helpers.constructor_parsing", "scrapers.columns.helpers.constructor_parsing"),
    ("scrapers.base.table.columns.helpers.driver_parsing", "scrapers.columns.helpers.driver_parsing"),
    ("scrapers.base.table.columns.helpers.engine_parsing", "scrapers.columns.helpers.engine_parsing"),
    ("scrapers.base.table.columns.helpers.link_lookup", "scrapers.columns.helpers.link_lookup"),
    ("scrapers.base.table.columns.helpers.results_parsing", "scrapers.columns.helpers.results_parsing"),
    ("scrapers.base.table.columns.types.auto", "scrapers.columns.types.auto"),
    ("scrapers.base.table.columns.types.br_list", "scrapers.columns.types.br_list"),
    ("scrapers.base.table.columns.types.constructor_base", "scrapers.columns.types.constructor.base"),
    ("scrapers.base.table.columns.types.constructor_part", "scrapers.columns.types.constructor.part"),
    ("scrapers.base.table.columns.types.date", "scrapers.columns.types.date"),
    ("scrapers.base.table.columns.types.engine", "scrapers.columns.types.engine"),
    ("scrapers.base.table.columns.types.entrant", "scrapers.columns.types.entrant"),
    ("scrapers.base.table.columns.types.links_list", "scrapers.columns.types.links_list"),
    ("scrapers.base.table.columns.types.list", "scrapers.columns.types.list"),
    ("scrapers.base.table.columns.types.multi", "scrapers.columns.types.multi.multi"),
    ("scrapers.base.table.columns.types.parsed_value", "scrapers.columns.types.parsed_value"),
    ("scrapers.base.table.columns.types.points", "scrapers.columns.types.points"),
    ("scrapers.base.table.columns.types.position", "scrapers.columns.types.position"),
    ("scrapers.base.table.columns.types.seasons", "scrapers.columns.types.seasons"),
    ("scrapers.base.table.columns.types.skip", "scrapers.columns.types.skip"),
    ("scrapers.base.table.columns.types.text", "scrapers.columns.types.text"),
    ("scrapers.base.table.columns.types.time", "scrapers.columns.types.time"),
    ("scrapers.base.transformers", "scrapers.transformers.record.fatalities_car"),

    # scrapers.wiki.* → scrapers.*
    ("scrapers.wiki.parsers.base", "scrapers.parsers.wiki.base"),
    ("scrapers.wiki.parsers.body_content", "scrapers.parsers.wiki.body_content"),
    ("scrapers.wiki.parsers.category_links", "scrapers.parsers.wiki.category_links"),
    ("scrapers.wiki.parsers.content_text", "scrapers.parsers.wiki.content_text"),
    ("scrapers.wiki.parsers.elements.figure", "scrapers.parsers.wiki.figure"),
    ("scrapers.wiki.parsers.elements.infobox", "scrapers.parsers.wiki.infobox"),
    ("scrapers.wiki.parsers.elements.list", "scrapers.parsers.wiki.base"),
    ("scrapers.wiki.parsers.elements.navbox", "scrapers.parsers.wiki.navbox"),
    ("scrapers.wiki.parsers.elements.paragraph", "scrapers.parsers.wiki.paragraph"),
    ("scrapers.wiki.parsers.elements.parsers", "scrapers.parsers.wiki.element"),
    ("scrapers.wiki.parsers.elements.references_wrap", "scrapers.parsers.wiki.references_wrap"),
    ("scrapers.wiki.parsers.elements.table", "scrapers.parsers.wiki.table"),
    ("scrapers.wiki.parsers.header", "scrapers.parsers.wiki.header"),
    ("scrapers.wiki.parsers.sections.adapter", "scrapers.parsers.section.wiki.adapter"),
    ("scrapers.wiki.parsers.sections.data_classes", "scrapers.parsers.section.match.priorities"),
    ("scrapers.wiki.parsers.sections.detection", "scrapers.parsers.section.wiki.detection"),
    ("scrapers.wiki.parsers.sections.helpers", "scrapers.parsers.section.wiki.helpers"),
    ("scrapers.wiki.parsers.sections.normalization", "scrapers.parsers.section.wiki.normalization"),
    ("scrapers.wiki.parsers.sections.section", "scrapers.parsers.section.wiki"),
    ("scrapers.wiki.parsers.sections.sub_section", "scrapers.parsers.wiki.sublevels.sub_section"),
    ("scrapers.wiki.parsers.sections.sub_sub_section", "scrapers.parsers.wiki.sublevels.sub_sub_section"),
    ("scrapers.wiki.parsers.sections.sub_sub_sub_section", "scrapers.parsers.wiki.sublevels.sub_sub_sub_section"),
    ("scrapers.wiki.scraper_wiki", "scrapers.scraper_wiki"),
    ("scrapers.wiki.component_metadata_wiki", "scrapers.component_metadata_wiki"),
    ("scrapers.wiki.constants_wiki", "scrapers.constants_wiki"),
    ("scrapers.wiki.discovery_wiki", "scrapers.discovery_wiki"),
    ("scrapers.wiki.drivers_checkpoint_flow_wiki", "scrapers.drivers_checkpoint_flow_wiki"),
    ("scrapers.wiki.seed_l0_compat_wiki", "scrapers.seed_l0_compat_wiki"),
    ("scrapers.wiki.seed_section_orchestration_flow_wiki", "scrapers.seed_section_orchestration_flow_wiki"),
    ("scrapers.wiki.sources_registry_wiki", "scrapers.sources_registry_wiki"),
    ("scrapers.wiki.parsers", "scrapers.parsers.wiki"),
    ("scrapers.wiki", "scrapers"),  # catch-all - must be last

    # scrapers.circuits.circuits_* → scrapers.circuits_*
    ("scrapers.circuits.circuits_complete_scraper", "scrapers.circuits_complete_scraper"),
    ("scrapers.circuits.circuits_helpers", "complete_extractor.export"),
    ("scrapers.circuits.circuits_infobox.services.entity_parsing", "scrapers.parsers.infobox.text_utils.circuit.text_processing.entity.base"),
    ("scrapers.circuits.circuits_infobox.services.entities", "scrapers.parsers.infobox.text_utils.circuit.text_processing.entity.base"),
    ("scrapers.circuits.circuits_infobox.services.geo", "scrapers.parsers.infobox.text_utils.circuit.geo"),
    ("scrapers.circuits.circuits_infobox.services.history", "scrapers.parsers.infobox.text_utils.circuit.history"),
    ("scrapers.circuits.circuits_infobox.services.lap_record", "scrapers.parsers.infobox.text_utils.circuit.lap_record"),
    ("scrapers.circuits.circuits_infobox.services.layouts", "scrapers.parsers.infobox.text_utils.circuit.layouts"),
    ("scrapers.circuits.circuits_infobox.services.specs", "scrapers.parsers.infobox.text_utils.circuit.specs"),
    ("scrapers.circuits.circuits_infobox.services.text_processing", "scrapers.parsers.infobox.text_utils.circuit.text_processing"),
    ("scrapers.circuits.circuits_infobox.services.text_utils", "scrapers.parsers.infobox.text_utils.base"),
    ("scrapers.circuits.circuits_infobox.services", "scrapers.parsers.infobox.text_utils.circuit"),
    ("scrapers.circuits.circuits_infobox.scraper", "scrapers.parsers.infobox.circuit"),
    ("scrapers.circuits.circuits_infobox.service", "scrapers.infobox.extraction.service.base_infobox_orchestrator"),
    ("scrapers.circuits.circuits_list_scraper", "scrapers.circuits_list_scraper"),
    ("scrapers.circuits.circuits_sections.layout_history", "scrapers.parsers.section.circuit.layout_history"),
    ("scrapers.circuits.columns.circuit_name_status", "scrapers.columns.types.multi.name_status_column.circuit"),

    # scrapers.drivers.* → scrapers.*
    ("scrapers.drivers.complete_scraper_drivers", "scrapers.complete_scraper_drivers"),
    ("scrapers.drivers.composition_drivers", "scrapers.wiring.composition_drivers"),
    ("scrapers.drivers.constants_drivers", "scrapers.constants_drivers"),
    ("scrapers.drivers.drivers_columns.driver_name_status", "scrapers.columns.types.multi.name_status_column.driver"),
    ("scrapers.drivers.drivers_columns.entries_starts", "scrapers.columns.types.entries_starts"),
    ("scrapers.drivers.drivers_columns.fatality_date", "scrapers.columns.types.fatality_date"),
    ("scrapers.drivers.drivers_columns.fatality_event", "scrapers.columns.types.fatality_event"),
    ("scrapers.drivers.drivers_columns.points_or_text", "scrapers.columns.types.points_or_text"),
    ("scrapers.drivers.drivers_columns.round", "scrapers.columns.types.round"),
    ("scrapers.drivers.drivers_helpers", "complete_extractor.export"),
    ("scrapers.drivers.drivers_infobox.parsers.active_years", "scrapers.parsers.infobox.field.active_years"),
    ("scrapers.drivers.drivers_infobox.parsers.car_numbers", "scrapers.parsers.infobox.field.car_numbers"),
    ("scrapers.drivers.drivers_infobox.parsers.cell", "scrapers.parsers.infobox.driver_cell"),
    ("scrapers.drivers.drivers_infobox.parsers.collapsible_table", "scrapers.parsers.infobox.collapsible_table"),
    ("scrapers.drivers.drivers_infobox.parsers.numeric", "scrapers.parsers.numeric_extractor"),
    ("scrapers.drivers.drivers_infobox.parsers.teams", "scrapers.parsers.infobox.field.teams"),
    ("scrapers.drivers.drivers_infobox.scraper", "scrapers.parsers.infobox.driver"),
    ("scrapers.drivers.drivers_sections", "scrapers.driver_results_schema_factory"),
    ("scrapers.drivers.female_drivers_list", "scrapers.female_drivers_list"),

    # scrapers.grands_prix.* → scrapers.*
    ("scrapers.grands_prix.columns_grands_prix.circuit_location", "scrapers.columns.types.function.circuit_location"),
    ("scrapers.grands_prix.columns_grands_prix.constructor_split", "scrapers.columns.types.multi.constructor_split"),
    ("scrapers.grands_prix.columns_grands_prix.race_title_status", "scrapers.columns.types.multi.name_status_column.race_title_status"),
    ("scrapers.grands_prix.complete_scraper_grands_prix", "scrapers.complete_scraper_grands_prix"),
    ("scrapers.grands_prix.list_scraper_grands_prix", "scrapers.list_scraper_grands_prix"),
    ("scrapers.grands_prix.mappers_grands_prix.by_year_record", "scrapers.records.mappers.grand_prix_by_year"),
    ("scrapers.grands_prix.sections_grands_prix.by_year", "scrapers.parsers.section.grand_prix.by_year"),
    ("scrapers.grands_prix.single_scraper_grands_prix", "scrapers.single_scraper_grands_prix"),

    # scrapers.constructors.* → scrapers.*
    ("scrapers.constructors.constructors_columns.constructor", "scrapers.columns.types.constructor.constructor"),
    ("scrapers.constructors.constructors_complete_scraper", "scrapers.constructors_complete_scraper"),
    ("scrapers.constructors.constructors_helpers.export", "complete_extractor.export"),
    ("scrapers.constructors.constructors_infobox.service", "scrapers.infobox.extraction.service.constructor"),
    ("scrapers.constructors.constructors_list", "scrapers.constructors_list"),
    ("scrapers.constructors.constructors_postprocess.assembler", "scrapers.records.dto.constructor"),
    ("scrapers.constructors.constructors_sections.history", "scrapers.parsers.section.table.constructor.history"),
    ("scrapers.constructors.constructors_sections.list_section", "scrapers.parsers.section.constructors.base"),
    ("scrapers.constructors.constructors_sections.service", "scrapers.services.section.extraction.constructor"),
    ("scrapers.constructors.constructors_single_scraper", "scrapers.constructors_single_scraper"),

    # scrapers.points.* → scrapers.*
    ("scrapers.points.base_points_scraper", "scrapers.base_points_scraper"),
    ("scrapers.points.columns_points.first_place", "scrapers.columns.types.first_place"),
    ("scrapers.points.helpers_points.parsers", "scrapers.parsers.helpers"),
    ("scrapers.points.parsers_points", "scrapers.parsers_points"),
    ("scrapers.points.points_scraper", "scrapers.scraper_table"),

    # scrapers.tyres.* → scrapers.*
    ("scrapers.tyres.columns_tyes.append_links", "scrapers.columns.types.append_links"),
    ("scrapers.tyres.list_scraper_tyres", "scrapers.list_scraper_tyres"),

    # scrapers.seasons.columns_seasons.* → scrapers.columns.*
    ("scrapers.seasons.columns_seasons.calendar_circuit", "scrapers.columns.types.calendar_circuit"),
    ("scrapers.seasons.columns_seasons.date_range", "scrapers.columns.types.date_range"),
    ("scrapers.seasons.columns_seasons.driver_rounds", "scrapers.columns.types.driver_rounds"),
    ("scrapers.seasons.columns_seasons.helpers.constants", "scrapers.columns.helpers.constants"),
    ("scrapers.seasons.columns_seasons.helpers.race_result.rules.context", "scrapers.columns.helpers.race_result.rules.context"),
    ("scrapers.seasons.columns_seasons.helpers.race_result.rules", "scrapers.columns.helpers.race_result.rules"),
    ("scrapers.seasons.columns_seasons.helpers.race_result", "scrapers.columns.helpers.race_result"),
    ("scrapers.seasons.columns_seasons.race_result", "scrapers.columns.types.race_result"),
    ("scrapers.seasons.helpers_seasons", "scrapers.helpers_seasons"),
    ("scrapers.seasons.list_scraper_seasons", "scrapers.parsers.wiki.seasons_list"),
    ("scrapers.seasons.parsers_seasons.cancelled_rounds", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.cancelled_rounds"),
    ("scrapers.seasons.parsers_seasons.entries", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.entries"),
    ("scrapers.seasons.parsers_seasons.entry_merger", "scrapers.parsers.entry_merger"),
    ("scrapers.seasons.parsers_seasons.free_practice", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.free_practice"),
    ("scrapers.seasons.parsers_seasons.results", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.results"),
    ("scrapers.seasons.parsers_seasons.standings", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base"),
    ("scrapers.seasons.parsers_seasons.table", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.table"),
    ("scrapers.seasons.parsers_seasons.testing_venues", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.testing_venues"),
    ("scrapers.seasons.parsers_seasons", "scrapers.parsers.wiki.seasons_wiki_table_element_parser_base"),
    ("scrapers.seasons.postprocess_seasons.assembler", "scrapers.records.dto.season"),
    ("scrapers.seasons.sections_seasons.service", "scrapers.services.section.extraction.season_text"),
    ("scrapers.seasons.sections_seasons", "scrapers.parsers.section.changes.season"),
    ("scrapers.seasons.services_seasons.domain_parsing_policy", "scrapers.domain_parsing_policy"),
    ("scrapers.seasons.single_scraper_seasons", "scrapers.single_scraper_seasons"),

    # scrapers.sponsorship_liveries.* → scrapers.*
    ("scrapers.sponsorship_liveries.columns_sponsorship_liveries.colour", "scrapers.columns.types.colour"),
    ("scrapers.sponsorship_liveries.columns_sponsorship_liveries.seasons", "scrapers.columns.types.sponsorship_seasons"),
    ("scrapers.sponsorship_liveries.columns_sponsorship_liveries.sponsor", "scrapers.columns.types.sponsor"),
    ("scrapers.sponsorship_liveries.helpers_sponsorship_liveries.paren_classifier", "scrapers.paren_classifier"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.grand_prix_scope", "scrapers.parsers.liveries.sponsorship.scope.grand_prix_transformer"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.record_text", "scrapers.sponsorship_record_text"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.scope_accumulators.grand_prix_scope", "scrapers.parsers.liveries.sponsorship.scope.accumulators.grand_prix"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.scope_handlers", "scrapers.parsers.liveries.sponsorship.scope.handlers"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters.record", "scrapers.parsers.liveries.sponsorship.splitters.record"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters", "scrapers.parsers.liveries.sponsorship.splitters"),
    ("scrapers.sponsorship_liveries.parsers_sponsorship_liveries", "scrapers.parsers.liveries.sponsorship"),
    ("scrapers.sponsorship_liveries.scraper_sponsorship_liveries", "scrapers.scraper_sponsorship_liveries"),

    # infrastructure.http_client.* → infrastructure.http.*
    ("infrastructure.http_client.caching.file", "infrastructure.cache.file.protocol"),
    ("infrastructure.http_client.caching.wiki_policy", "infrastructure.cache.wiki_policy"),
    ("infrastructure.http_client.clients.urllib_http", "infrastructure.http.clients.urllib_http"),
    ("infrastructure.http_client.components", "infrastructure.http.request_executor"),
    ("infrastructure.http_client.config", "infrastructure.http.config"),
    ("infrastructure.http_client.factories", "infrastructure.http.factories.default_policy"),
    ("infrastructure.http_client.interfaces", "infrastructure.http.protocols.client"),
    ("infrastructure.http_client.policies.default_retry", "infrastructure.http.policies.retry.default"),
    ("infrastructure.http_client.policies.http", "infrastructure.http.policies.http"),
    ("infrastructure.http_client.policies.response_cache", "infrastructure.http.protocols.text_cache"),
    ("infrastructure.http_client.requests_shim.http_error", "infrastructure.http.errors.shim.http"),
    ("infrastructure.http_client.requests_shim.http_shim_error", "infrastructure.http.errors.shim.base"),
    ("infrastructure.http_client.requests_shim.request_error", "infrastructure.http.errors.base"),
    ("infrastructure.http_client.requests_shim.response", "infrastructure.http.response"),
    ("infrastructure.cache.file_ttl", "infrastructure.cache.file.ttl"),
    ("infrastructure.gemini.model_config", "infrastructure.gemini.model.config"),
    ("infrastructure.gemini.model_selector", "infrastructure.gemini.model.selector"),

    # models
    ("models.value_objects.normalized_date", "models.value_objects.date.normalized"),
    ("models.value_objects.date", "models.value_objects.date.base"),
    ("models.validation.engine_regulation", "models.validation.engine.regulation"),

    # config
    ("config.app_config_provider", "config.app.provider"),

    # layers
    ("layers.orchestration.runners.function_export", "layers.runners.layer_job.function_export"),
    ("layers.orchestration.runners.grand_prix", "layers.runners.layer_job.grand_prix"),
    ("layers.path_resolver", "path_resolver.helpers"),
    ("layers.zero.executor", "layers.executors.zero"),
    ("layers.composition", "wiki_pipeline.create_default.applications"),

    # scrapers import as aliases
    ("scrapers.base import contracts", "scrapers import contracts"),
]

# Special name remaps (class/function renames in the same file)
NAME_REMAPS = {
    "NumericParser": "NumericExtractor",
    "SectionMatchPriorities": "SectionMatchPriorities",  # unchanged - check location
    "FileTtlCache": "FileTtlCache",
    "FileTtlCacheAdapter": "FileTtlCacheAdapter",
    "GeminiJsonFileCacheAdapter": "GeminiJsonFileCacheAdapter",
    "HttpResponseFileCacheAdapter": "HttpResponseFileCacheAdapter",
    "DriverResultsSchemaFactory": "DriverResultsSchemaFactory",
    "ConstructorRecordDTO": "ConstructorRecordDTO",
    "DriverRecordDTO": "DriverRecordDTO",
    "SeasonPayloadDTO": "SeasonPayloadDTO",
    "SeasonRecordSections": "SeasonRecordSections",
    "SeasonRecordAssembler": "SeasonRecordAssembler",
}

# Additional name-mapping: when module changes, these class/func renames apply
MODULE_RENAMES = {
    # old_module → {old_name: new_name}
    "scrapers.drivers.drivers_infobox.parsers.numeric": {"NumericParser": "NumericExtractor"},
    "scrapers.drivers.drivers_sections": {"DriverResultsSchemaFactory": "DriverResultsSchemaFactory"},
    "scrapers.seasons.list_scraper_seasons": {
        "SeasonsSectionParser": "SeasonsSectionParser",
        "SeasonsTableParser": "SeasonsTableParser",
    },
    "scrapers.seasons.postprocess_seasons.assembler": {
        "SeasonPayloadDTO": "SeasonPayloadDTO",
        "SeasonRecordAssembler": "SeasonRecordAssembler", 
        "SeasonRecordSections": "SeasonRecordSections",
    },
    "scrapers.constructors.constructors_postprocess.assembler": {
        "ConstructorRecordDTO": "ConstructorRecordDTO",
    },
    "scrapers.drivers.drivers_helpers": {
        "export": "export",  # module rename only - export stays as submodule
    },
    "scrapers.circuits.circuits_helpers": {
        "export": "export",
    },
    "scrapers.constructors.constructors_helpers.export": {
        "constructor_name_initial": "constructor_name_initial",
    },
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for old, new in MAPPINGS:
        # Replace in import statements: "from OLD import" and "import OLD"
        content = content.replace(f"from {old} import", f"from {new} import")
        content = content.replace(f"from {old}\n", f"from {new}\n")
        # Replace "import OLD" at start of line
        content = re.sub(rf'^import {re.escape(old)}(\s|$)', f'import {new}\\1', content, flags=re.MULTILINE)
        # Replace "import OLD as"
        content = re.sub(rf'^import {re.escape(old)} as ', f'import {new} as ', content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Process all test files
test_dir = Path('tests')
changed = 0
for f in test_dir.rglob('*.py'):
    if fix_file(str(f)):
        changed += 1

print(f"Fixed {changed} files")
