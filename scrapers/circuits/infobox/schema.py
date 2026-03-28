from scrapers.base.infobox.dsl import InfoboxSchemaDSL
from scrapers.base.infobox.dsl import field

CIRCUIT_INFOBOX_SCHEMA = InfoboxSchemaDSL(
    name="circuit.infobox",
    fields=[
        field("location", ("Location",)),
        field("coordinates", ("Coordinates",)),
        field("fia_grade", ("FIA Grade",)),
        field("length", ("Length",)),
        field("turns", ("Turns",)),
        field("race_lap_record", ("Race lap record",)),
        field("opened", ("Opened",)),
        field("closed", ("Closed",)),
        field("former_names", ("Former names",)),
        field("owner", ("Owner",)),
        field("operator", ("Operator",)),
        field("capacity", ("Capacity",)),
        field("broke_ground", ("Broke ground",)),
        field("built", ("Built",)),
        field("construction_cost", ("Construction cost",)),
        field("website", ("Website",)),
        field("area", ("Area",)),
        field("major_events", ("Major events",)),
        field("address", ("Address",)),
        field("architect", ("Architect",)),
        field("surface", ("Surface",)),
        field("banking", ("Banking",)),
    ],
).build()
