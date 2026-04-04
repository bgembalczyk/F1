from scrapers.base.infobox.dsl import InfoboxFieldSpec
from scrapers.base.infobox.dsl import InfoboxSchemaDSL

CIRCUIT_INFOBOX_SCHEMA = InfoboxSchemaDSL(
    name="circuit.infobox",
    fields=[
        InfoboxFieldSpec("location", ("Location",)),
        InfoboxFieldSpec("coordinates", ("Coordinates",)),
        InfoboxFieldSpec("fia_grade", ("FIA Grade",)),
        InfoboxFieldSpec("length", ("Length",)),
        InfoboxFieldSpec("turns", ("Turns",)),
        InfoboxFieldSpec("race_lap_record", ("Race lap record",)),
        InfoboxFieldSpec("opened", ("Opened",)),
        InfoboxFieldSpec("closed", ("Closed",)),
        InfoboxFieldSpec("former_names", ("Former names",)),
        InfoboxFieldSpec("owner", ("Owner",)),
        InfoboxFieldSpec("operator", ("Operator",)),
        InfoboxFieldSpec("capacity", ("Capacity",)),
        InfoboxFieldSpec("broke_ground", ("Broke ground",)),
        InfoboxFieldSpec("built", ("Built",)),
        InfoboxFieldSpec("construction_cost", ("Construction cost",)),
        InfoboxFieldSpec("website", ("Website",)),
        InfoboxFieldSpec("area", ("Area",)),
        InfoboxFieldSpec("major_events", ("Major events",)),
        InfoboxFieldSpec("address", ("Address",)),
        InfoboxFieldSpec("architect", ("Architect",)),
        InfoboxFieldSpec("surface", ("Surface",)),
        InfoboxFieldSpec("banking", ("Banking",)),
    ],
).build()
