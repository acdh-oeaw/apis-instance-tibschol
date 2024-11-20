from apis_core.relations.forms import RelationForm
from django import forms
from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm
from django.apps import apps
from parler.fields import TranslatedField
from parler.forms import TranslatableModelForm


class TibscholEntityForm(GenericModelForm):
    class Meta:
        exclude = ["published"]
        widgets = {
            "notes": forms.TextInput(
                attrs={"placeholder": "Do not use this field, it will be dropped soon."}
            ),
        }


class TibScholRelationMixinForm(RelationForm):
    # position the subject/object field on top
    field_order = ["subj", "subj_ct_and_id", "obj", "obj_ct_and_id"]


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


class PersonForm(TranslatableModelForm, TibscholEntityForm):
    name = TranslatedField()

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].help_text = (
            "Equivalent transliterations in Tibetan/English inputs will be automatically provided at the time of creation. However, updates to this field will NOT trigger any updates to the values in other languages."
        )


class WorkForm(TibscholEntityForm):
    field_order = [
        "name",
        "alternative_names",
        "original_language",
        "subject_vocab",
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
        "dimension",
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
        "subject_vocab",
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
