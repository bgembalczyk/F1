from typing import Final

from models.records.base_factory import BaseRecordFactory
from models.records.factories.car_factory import CarRecordFactory
from models.records.factories.circuit_complete_factory import CircuitCompleteRecordFactory
from models.records.factories.circuit_details_factory import CircuitDetailsRecordFactory
from models.records.factories.circuit_factory import CircuitRecordFactory
from models.records.factories.constructor_factory import ConstructorRecordFactory
from models.records.factories.driver_factory import DriverRecordFactory
from models.records.factories.drivers_championships_factory import DriversChampionshipsRecordFactory
from models.records.factories.engine_manufacturer_factory import EngineManufacturerRecordFactory
from models.records.factories.event_factory import EventRecordFactory
from models.records.factories.fatality_factory import FatalityRecordFactory
from models.records.factories.grands_prix_factory import GrandsPrixRecordFactory
from models.records.factories.link_factory import LinkRecordFactory
from models.records.factories.season_factory import SeasonRecordFactory
from models.records.factories.season_summary_factory import SeasonSummaryRecordFactory
from models.records.factories.special_driver_factory import SpecialDriverRecordFactory
from models.records.field_normalizer import FieldNormalizer


NORMALIZER: Final[FieldNormalizer] = FieldNormalizer()
FACTORY_REGISTRY: Final[dict[str, BaseRecordFactory]] = {
    "link": LinkRecordFactory(NORMALIZER),
    "season": SeasonRecordFactory(NORMALIZER),
    "drivers_championships": DriversChampionshipsRecordFactory(NORMALIZER),
    "driver": DriverRecordFactory(NORMALIZER),
    "special_driver": SpecialDriverRecordFactory(NORMALIZER),
    "constructor": ConstructorRecordFactory(NORMALIZER),
    "circuit": CircuitRecordFactory(NORMALIZER),
    "event": EventRecordFactory(NORMALIZER),
    "car": CarRecordFactory(NORMALIZER),
    "fatality": FatalityRecordFactory(NORMALIZER),
    "season_summary": SeasonSummaryRecordFactory(NORMALIZER),
    "grands_prix": GrandsPrixRecordFactory(NORMALIZER),
    "circuit_details": CircuitDetailsRecordFactory(NORMALIZER),
    "circuit_complete": CircuitCompleteRecordFactory(NORMALIZER),
    "engine_manufacturer": EngineManufacturerRecordFactory(NORMALIZER),
}
