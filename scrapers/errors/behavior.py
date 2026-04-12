from enum import Enum

from scrapers.errors.category import ErrorCategory


class ErrorBehavior(str, Enum):
    SOFT = "soft"
    HARD = "hard"


ERROR_BEHAVIOR_BY_CATEGORY: dict[ErrorCategory, ErrorBehavior] = {
    ErrorCategory.NETWORK: ErrorBehavior.HARD,
    ErrorCategory.PARSE: ErrorBehavior.HARD,
    ErrorCategory.VALIDATION: ErrorBehavior.HARD,
    ErrorCategory.DOMAIN: ErrorBehavior.SOFT,
}



