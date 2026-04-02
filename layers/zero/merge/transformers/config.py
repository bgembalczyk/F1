from __future__ import annotations

from collections.abc import Callable

from scrapers.wiki.constants import TYRE_MANUFACTURERS_SOURCE

from .base import DomainTransformStrategy
from .circuits import CircuitsDomainTransformStrategy
from .constructors import ConstructorDomainTransformStrategy
from .drivers import DriversDomainTransformStrategy
from .engines import EnginesDomainTransformStrategy
from .grands_prix import GrandsPrixDomainTransformStrategy
from .races import RacesDomainTransformStrategy
from .seasons import TyreManufacturersTransformStrategy
from .teams import TeamsDomainTransformStrategy

TransformHandler = Callable[[str, str, dict[str, object]], dict[str, object]]
DEFAULT_SOURCE_PIPELINE = "*"


class StrategyHandlerAdapter:
    def __init__(self, strategy_factory: Callable[[str], DomainTransformStrategy]) -> None:
        self._strategy_factory = strategy_factory

    def __call__(self, domain: str, source_name: str, record: dict[str, object]) -> dict[str, object]:
        strategy = self._strategy_factory(domain)
        return strategy.transform(record, source_name)


def _single_instance_factory(strategy: DomainTransformStrategy) -> Callable[[str], DomainTransformStrategy]:
    return lambda _domain: strategy


_TYRE_MANUFACTURERS_STRATEGY = TyreManufacturersTransformStrategy()
_CIRCUITS_STRATEGY = CircuitsDomainTransformStrategy()
_ENGINES_STRATEGY = EnginesDomainTransformStrategy()
_GRANDS_PRIX_STRATEGY = GrandsPrixDomainTransformStrategy()
_TEAMS_STRATEGY = TeamsDomainTransformStrategy()
_DRIVERS_STRATEGY = DriversDomainTransformStrategy()
_RACES_STRATEGY = RacesDomainTransformStrategy()

_tyre_manufacturers_handler = StrategyHandlerAdapter(_single_instance_factory(_TYRE_MANUFACTURERS_STRATEGY))
_constructor_domain_handler = StrategyHandlerAdapter(ConstructorDomainTransformStrategy)
_circuits_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_CIRCUITS_STRATEGY))
_engines_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_ENGINES_STRATEGY))
_grands_prix_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_GRANDS_PRIX_STRATEGY))
_teams_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_TEAMS_STRATEGY))
_drivers_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_DRIVERS_STRATEGY))
_races_domain_handler = StrategyHandlerAdapter(_single_instance_factory(_RACES_STRATEGY))

TRANSFORM_STRATEGY_PIPELINES: dict[str, dict[str, tuple[TransformHandler, ...]]] = {
    "*": {
        TYRE_MANUFACTURERS_SOURCE: (_tyre_manufacturers_handler,),
    },
    "constructors": {
        DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
    },
    "constructor": {
        DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
    },
    "chassis": {
        DEFAULT_SOURCE_PIPELINE: (_constructor_domain_handler,),
    },
    "circuits": {
        DEFAULT_SOURCE_PIPELINE: (_circuits_domain_handler,),
    },
    "engines": {
        DEFAULT_SOURCE_PIPELINE: (_engines_domain_handler,),
    },
    "grands_prix": {
        DEFAULT_SOURCE_PIPELINE: (_grands_prix_domain_handler,),
    },
    "teams": {
        DEFAULT_SOURCE_PIPELINE: (_teams_domain_handler,),
    },
    "drivers": {
        DEFAULT_SOURCE_PIPELINE: (_drivers_domain_handler,),
    },
    "races": {
        DEFAULT_SOURCE_PIPELINE: (_races_domain_handler,),
    },
}


def resolve_record_transform_handlers(domain: str, source_name: str) -> tuple[TransformHandler, ...]:
    global_handlers = TRANSFORM_STRATEGY_PIPELINES.get("*", {})
    domain_handlers = TRANSFORM_STRATEGY_PIPELINES.get(domain, {})

    resolved: list[TransformHandler] = [
        *global_handlers.get(DEFAULT_SOURCE_PIPELINE, ()),
        *global_handlers.get(source_name, ()),
    ]
    domain_pipeline = domain_handlers.get(source_name)
    if domain_pipeline is None:
        domain_pipeline = domain_handlers.get(DEFAULT_SOURCE_PIPELINE, ())
    resolved.extend(domain_pipeline)
    return tuple(resolved)
