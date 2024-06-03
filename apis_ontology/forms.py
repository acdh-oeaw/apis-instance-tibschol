from apis_core.generic.forms import GenericFilterSetForm


class PlaceSearchForm(GenericFilterSetForm):
    field_order = [
        "columns",
        "label",
        "alternative_names",
        "start_date_written",
        "comments",
        "notes",
        "external_links",
    ]
