from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import Protocol
from typing import TypeVar

from scrapers.wiki.component_metadata import ComponentMetadata


class DiscoveryComponentProtocol(Protocol):
    @property
    def cls(self) -> type[object]: ...

    @property
    def metadata(self) -> ComponentMetadata: ...


class RegistryEntryProtocol(Protocol):
    @property
    def seed_name(self) -> str: ...

    @property
    def wikipedia_url(self) -> str: ...

    @property
    def output_category(self) -> str: ...


class SeedPathRegistryEntryProtocol(RegistryEntryProtocol, Protocol):
    @property
    def default_output_path(self) -> str: ...

    @property
    def legacy_output_path(self) -> str: ...


class ListJobPathRegistryEntryProtocol(RegistryEntryProtocol, Protocol):
    @property
    def json_output_path(self) -> str: ...

    @property
    def legacy_json_output_path(self) -> str: ...


RegistryEntryT = TypeVar("RegistryEntryT", bound=RegistryEntryProtocol)


@dataclass(frozen=True)
class RegistryValidationRule(Generic[RegistryEntryT]):
    label: str
    extractor: Callable[[RegistryEntryT], str]
    expected_prefix: Callable[[RegistryEntryT], str]
    message: Callable[[RegistryEntryT], str]


@dataclass(frozen=True)
class RegistryValidationSpec(Generic[RegistryEntryT]):
    duplicate_message: Callable[[str], str]
    empty_url_message: Callable[[str], str]
    path_rules: tuple[RegistryValidationRule[RegistryEntryT], ...]
