"""Backward-compatible import bridge for legacy pipeline mixin path."""

from scrapers.mixins.compat_aliases import DebugDumpMixin
from scrapers.mixins.compat_aliases import RetryMixin
from scrapers.mixins.compat_aliases import ValidationMixin

__all__ = ["RetryMixin", "DebugDumpMixin", "ValidationMixin"]
