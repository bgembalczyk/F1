from scrapers.infobox.schemas.dsl import InfoboxFieldSpec
from scrapers.infobox.schemas.dsl import InfoboxSchemaDSL

DRIVER_GENERAL_SCHEMA = InfoboxSchemaDSL(
    name="driver.general",
    fields=[
        InfoboxFieldSpec("born", ("Born",), parser="date_place"),
        InfoboxFieldSpec("died", ("Died",), parser="date_place"),
        InfoboxFieldSpec(
            "parents",
            ("Parent", "Parents", "Parent(s)"),
            parser="relations",
        ),
        InfoboxFieldSpec("relatives", ("Relatives",), parser="relations"),
        InfoboxFieldSpec("children", ("Children",), parser="links"),
        InfoboxFieldSpec("cause_of_death", ("Cause of death",), parser="text"),
    ],
).build()


__all__ = ["DRIVER_GENERAL_SCHEMA"]
