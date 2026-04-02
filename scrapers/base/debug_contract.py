from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from logging import DEBUG
from logging import INFO
from logging import WARNING


class DebugMode(str, Enum):
    OFF = "off"
    VERBOSE = "verbose"
    TRACE = "trace"


@dataclass(frozen=True)
class DebugModeContract:
    mode: DebugMode
    log_level: int
    verbosity: int
    writes_debug_dumps: bool
    enforces_debug_output_path: bool


DEBUG_MODE_CONTRACT: dict[DebugMode, DebugModeContract] = {
    DebugMode.OFF: DebugModeContract(
        mode=DebugMode.OFF,
        log_level=WARNING,
        verbosity=0,
        writes_debug_dumps=False,
        enforces_debug_output_path=False,
    ),
    DebugMode.VERBOSE: DebugModeContract(
        mode=DebugMode.VERBOSE,
        log_level=INFO,
        verbosity=1,
        writes_debug_dumps=False,
        enforces_debug_output_path=False,
    ),
    DebugMode.TRACE: DebugModeContract(
        mode=DebugMode.TRACE,
        log_level=DEBUG,
        verbosity=2,
        writes_debug_dumps=True,
        enforces_debug_output_path=True,
    ),
}


def resolve_debug_contract(mode: DebugMode) -> DebugModeContract:
    return DEBUG_MODE_CONTRACT[mode]
