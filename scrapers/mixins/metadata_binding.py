# MetadataBindingMixin removed. Functions inlined into scrapers.section.serializer.
# This file is kept for backward compatibility only.
from scrapers.section.serializer import bind_section_defaults
from scrapers.section.serializer import build_section_metadata

__all__ = ["bind_section_defaults", "build_section_metadata"]
