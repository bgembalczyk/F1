from scrapers.base.infobox.dsl import InfoboxSchemaDSL, field

DRIVER_GENERAL_SCHEMA = InfoboxSchemaDSL(
    name="driver.general",
    fields=[
        field("born", ("Born",), parser="date_place"),
        field("died", ("Died",), parser="date_place"),
        field(
            "parents",
            ("Parent", "Parents", "Parent(s)"),
            parser="relations",
        ),
        field("relatives", ("Relatives",), parser="relations"),
        field("children", ("Children",), parser="links"),
        field("cause_of_death", ("Cause of death",), parser="text"),
    ],
).build()
