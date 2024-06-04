from apis_core.generic.forms import GenericFilterSetForm


class PlaceSearchForm(GenericFilterSetForm):
    field_order = [
        "columns",
        "label",
        "start_date_written",
        "comments",
        "notes",
        "external_links",
    ]


class PersonSearchForm(GenericFilterSetForm):
    field_order = [
        "columns",
        "name",
        "start_date_written",
        "end_date_written",
        "gender",
        "nationality",
        "comments",
        "notes",
        "external_links",
    ]


class WorkSearchForm(GenericFilterSetForm):
    field_order = [
        "columns",
        "name",
        "original_language",
        "subject",
        "start_date_written",
        "sde_dge_ref",
        "isExtant",
        "comments",
        "external_links",
    ]
