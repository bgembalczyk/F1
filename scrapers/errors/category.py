from enum import Enum


class ErrorCategory(str, Enum):
    NETWORK = "network"
    PARSE = "parse"
    VALIDATION = "validation"
    DOMAIN = "domain"
