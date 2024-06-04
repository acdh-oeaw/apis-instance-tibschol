from django.utils.html import escape

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.generic.tables import GenericTable
from django_tables2.utils import A

from .models import Excerpts, Instance, Person, Place, TibScholRelationMixin, Work
from .templatetags.filter_utils import (
    render_coordinate,
    render_links,
    render_list_field,
)
from .templatetags.parse_comment import parse_comment

import django_tables2 as tables
import logging
from apis_core.apis_metainfo.models import RootObject

from django.utils.safestring import mark_safe
from django.urls import reverse

from lxml import etree

logger = logging.getLogger(__name__)


class PlaceTable(AbstractEntityTable):
    class Meta:
        model = Place
        fields = [
            "id",
            "label",
        ]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]

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
        ]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_external_links(self, value):
        return render_links(value)

    def render_alternative_names(self, value):
        return render_list_field(value)


class WorkTable(AbstractEntityTable):
    class Meta:
        model = Work
        fields = ["id", "name", "author"]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]
        row_attrs = {
            "style": lambda record: "background-color: lightgray;"
            if not record.isExtant
            else None
        }

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)


class InstanceTable(AbstractEntityTable):
    class Meta:
        model = Instance
        fields = ["id", "name", "start_date_written", "author"]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)

    def render_external_links(self, value):
        return render_links(value)

    def render_availability(self, value):
        symbol = "indeterminate_question_box"
        if value == "lost":
            symbol = "close"
        elif value == "non-accessible":
            symbol = "lock"
        elif value == "available":
            symbol = "check"
        return mark_safe(f'<span class="material-symbols-outlined">{symbol}</span>')


class RelationsTable(GenericTable):
    reverse = False

    name = tables.Column(verbose_name="Relationship")
    obj = tables.Column(verbose_name="Object")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the obj attribute based on the value of self.reverse
        xslt_file = "apis_ontology/xslt/teibp.xsl"
        xslt = etree.parse(xslt_file)
        self.transform = etree.XSLT(xslt)

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
        return mark_safe(parse_comment(render_list_field(value)))

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

    def render_tei_refs(self, value):
        delim = "\n" if "\n" in value else "," if "," in value else " "
        xml_ids = value.split(delim)
        links = []
        for xml_id in xml_ids:
            true_id = xml_id.replace('"', "").replace("xml:id=", "").strip()
            links.append(
                f"""<a href="#" onclick="showPopup('{true_id}'); return false;">{true_id}</a>"""
            )

        return mark_safe("<br />".join(links))


class RelationsTableEdit(RelationsTable):
    class Meta(GenericTable.Meta):
        model = TibScholRelationMixin
        fields = [
            "name",
            "obj",
            "support_notes",
            "zotero_refs",
            "tei_refs",
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
            "name",
            "obj",
            "support_notes",
            "zotero_refs",
            "tei_refs",
        ]
        exclude = ["view", "edit", "desc", "delete", "subj"]
