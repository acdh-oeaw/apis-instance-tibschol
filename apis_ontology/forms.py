from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm
from apis_core.relations.forms import RelationForm
from apis_core.apis_entities.forms import E53_PlaceForm
from django import forms


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


class PlaceForm(E53_PlaceForm):
    class Meta:
        exclude = ["published"]
        widgets = {
            "notes": forms.TextInput(
                attrs={"placeholder": "Do not use this field, it will be dropped soon."}
            ),
        }

    field_order = [
        "place",
        "label",
        "alternative_names",
        "start",
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
        "start",
        "end",
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
        "subject_vocab",
        "start",
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
        "start",
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


class TibScholEntityMixinSearchForm(GenericFilterSetForm):
    columns_exclude = [
        "start_date_from",
        "end_date_from",
        "start_date_sort",
        "start_date_to",
        "end_date_to",
        "end_date_sort",
        "rootobject_ptr",
        "self_contenttype",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Force override of the model BooleanField
        self.fields["review"] = forms.TypedChoiceField(
            label="Entity reviewed",
            choices=[
                ("", ""),
                ("true", "Yes"),
                ("false", "No"),
            ],
            widget=forms.Select,
            coerce=lambda v: {"true": True, "false": False}.get(v, None),
            required=False,
        )


class PlaceSearchForm(TibScholEntityMixinSearchForm):
    field_order = [
        "columns",
        "label",
        "start",
        "comments",
        "notes",
        "external_links",
    ]


class PersonSearchForm(TibScholEntityMixinSearchForm):
    field_order = [
        "columns",
        "name",
        "start",
        "end",
        "gender",
        "nationality",
        "comments",
        "notes",
        "external_links",
    ]


class WorkSearchForm(TibScholEntityMixinSearchForm):
    field_order = [
        "columns",
        "name",
        "original_language",
        "subject_vocab",
        "start",
        "sde_dge_ref",
        "isExtant",
        "comments",
        "external_links",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Force override of the model BooleanField
        self.fields["isExtant"] = forms.TypedChoiceField(
            label="Is extant?",
            choices=[
                ("", ""),
                ("true", "Yes"),
                ("false", "No"),
            ],
            widget=forms.Select,
            coerce=lambda v: {"true": True, "false": False}.get(v, None),
            required=False,
        )


class InstanceSearchForm(TibScholEntityMixinSearchForm):
    field_order = [
        "columns",
        "name",
        "start",
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


class RelationSearchForm(GenericFilterSetForm):
    columns_exclude = [
        "subj_object_id",
        "obj_object_id",
        "subj_content_type",
        "obj_content_type",
        "start_date_sort",
        "end_date_sort",
        "start_date_from",
        "start_date_to",
        "end_date_from",
        "end_date_to",
        "relation_ptr",
    ]
