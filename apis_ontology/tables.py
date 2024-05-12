import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.generic.tables import GenericTable
from django_tables2.utils import A

from .models import Instance, Person, Place, TibScholRelationMixin, Work
from .templatetags.filter_utils import render_coordinate, render_links
from .templatetags.parse_comment import parse_comment

import django_tables2 as tables
import logging
from apis_core.apis_metainfo.models import RootObject

from django.utils.safestring import mark_safe
from django.urls import reverse


logger = logging.getLogger(__name__)


class PlaceTable(AbstractEntityTable):
    class Meta:
        model = Place
        fields = [
            "id",
            "label",
            "start_date_written",
            "latitude",
            "longitude",
            "external_links",
        ]
        exclude = ["desc", "view"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_external_links(self, value):
        return render_links(value)

    def render_latitude(self, value):
        return render_coordinate(value)

    def render_longitude(self, value):
        return render_coordinate(value)


class PersonTable(AbstractEntityTable):
    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "start_date_written",
            "end_date_written",
            "external_links",
        ]
        exclude = ["desc"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_external_links(self, value):
        return render_links(value)


class WorkTable(AbstractEntityTable):
    class Meta:
        model = Work
        fields = ["id", "name", "sde_dge_ref", "author"]
        exclude = ["desc"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)


class InstanceTable(AbstractEntityTable):
    class Meta:
        model = Instance
        fields = ["id", "tibschol_ref", "name", "author", "external_links"]
        exclude = ["desc"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)

    def render_external_links(self, value):
        return render_links(value)


class RelationsTable(GenericTable):
    reverse = False

    name = tables.Column(verbose_name="Relationship")
    obj = tables.Column(verbose_name="Object")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the obj attribute based on the value of self.reverse

    def render_name(self, record):
        if self.context["object"].pk == record.subj.pk:
            return record.name
        elif self.context["object"].pk == record.obj.pk:
            return record.reverse_name
        else:
            return ""

    def render_support_notes(self, value):
        return mark_safe(parse_comment(value))

    def render_zotero_refs(self, value):
        return mark_safe(parse_comment(value))

    def render_obj(self, record):
        # return str(record) + str(self.context["object"].pk)
        if self.context["object"].pk == record.obj.pk:
            # return str(RootObject.objects_inheritance.get_subclass(pk=record.subj.pk))
            actual_obj = RootObject.objects_inheritance.get_subclass(pk=record.subj.pk)

        else:
            actual_obj = RootObject.objects_inheritance.get_subclass(pk=record.obj.pk)

        return mark_safe(
            "<a href='"
            + actual_obj.get_absolute_url()
            + "' target='_BLANK'>"
            + str(actual_obj)
            + "</a>"
        )


class RelationsTableEdit(RelationsTable):
    class Meta(GenericTable.Meta):
        model = TibScholRelationMixin
        fields = [
            "id",
            "name",
            "obj",
            "support_notes",
            "zotero_refs",
            "TEI",
            "edit",
            "delete",
        ]
        exclude = ["view", "desc", "subj"]

    edit = tables.TemplateColumn(
        "<a href='{% url 'apis:relationupdate' record.id %}' target=\"_BLANK\"><span class=\"material-symbols-outlined\">edit</span></a>"
    )

    delete = tables.TemplateColumn(
        "<a href='{% url 'apis:relationdelete' record.id %}?next={{ request.GET.next }}' target=\"_BLANK\"><span class=\"material-symbols-outlined\">delete</span></a>"
    )


class RelationsTableView(RelationsTable):
    class Meta(GenericTable.Meta):
        model = TibScholRelationMixin
        fields = [
            "id",
            "name",
            "obj",
            "support_notes",
            "zotero_refs",
            "TEI",
        ]
        exclude = ["view", "edit", "desc", "delete", "subj"]
