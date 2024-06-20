from django import forms
from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm


class TibscholEntityForm(GenericModelForm):
    class Meta:
        exclude = ["published"]
        widgets = {
            "notes": forms.TextInput(
                attrs={"placeholder": "Do not use this field, it will be dropped soon."}
            ),
        }


class TibScholRelationMixinForm(GenericModelForm):
    class Meta:
        exclude = []

    field_order = ["subj", "obj"]


class PlaceForm(TibscholEntityForm):
    field_order = [
        "label",
        "alternative_names",
        "start_date_written",
        "latitude",
        "longitude",
        "comments",
        "notes",
        "external_links",
        "review",
    ]


class PersonForm(TibscholEntityForm):
    field_order = [
        "name",
        "alternative_names",
        "start_date_written",
        "end_date_written",
        "gender",
        "nationality",
        "comments",
        "notes",
        "external_links",
        "review",
    ]


class WorkForm(TibscholEntityForm):
    field_order = [
        "name",
        "alternative_names",
        "original_language",
        "subject",
        "start_date_written",
        "sde_dge_ref",
        "isExtant",
        "comments",
        "notes",
        "external_links",
        "review",
    ]


class InstanceForm(TibscholEntityForm):
    field_order = [
        "name",
        "alternative_names",
        "start_date_written",
        "availability",
        "tibschol_ref",
        "set_num",
        "volume",
        "sb_text_number",
        "pp_kdsb",
        "num_folios",
        "signature_letter",
        "signature_number",
        "drepung_number",
        "provenance",
        "zotero_ref",
        "item_description",
        "comments",
        "notes",
        "external_links",
        "review",
    ]


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


class InstanceSearchForm(GenericFilterSetForm):
    field_order = [
        "columns",
        "name",
        "start_date_written",
        "availability",
        "tibschol_ref",
        "set_num",
        "volume",
        "sb_text_number",
        "pp_kdsb",
        "num_folios",
        "signature_letter",
        "signature_number",
        "drepung_number",
        "provenance",
        "zotero_ref",
        "item_description",
        "comments",
        "external_links",
    ]
