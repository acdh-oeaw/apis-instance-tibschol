from django.utils.html import escape

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.generic.tables import GenericTable
from django_tables2.utils import A
from django.template.loader import render_to_string

from .models import Excerpts, Instance, Person, Place, TibScholRelationMixin, Work
from .templatetags.filter_utils import (
    preview_text,
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


class TibscholEntityMixinTable(AbstractEntityTable):
    def render_alternative_names(self, value):
        return render_list_field(value)

    def render_external_links(self, value):
        return render_links(value)

    def render_comments(self, value):
        return mark_safe(parse_comment(value))

    id = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )


class PlaceTable(TibscholEntityMixinTable):
    class Meta:
        model = Place
        fields = [
            "id",
            "label",
        ]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]

    def render_latitude(self, value):
        return render_coordinate(value)

    def render_longitude(self, value):
        return render_coordinate(value)


class PersonTable(TibscholEntityMixinTable):
    class Meta:
        model = Person
        fields = [
            "id",
            "name",
        ]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]


class WorkTable(TibscholEntityMixinTable):
    class Meta:
        model = Work
        fields = ["id", "name", "author"]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]
        row_attrs = {
            "style": lambda record: "background-color: lightgray;"
            if not record.isExtant
            else None
        }

    author = tables.Column(
        verbose_name="Author", accessor="author_name", orderable=True
    )

    def render_author(self, record):
        context = {
            "entity_id": record.author_id,
            "entity_name": record.author_name,
            "entity_uri": f"/apis/apis_ontology.person/{record.author_id}",  # TODO: use urls
        }
        return mark_safe(
            render_to_string("apis_ontology/linked_entity_column.html", context)
        )


class InstanceTable(TibscholEntityMixinTable):
    class Meta:
        model = Instance
        fields = ["id", "name", "start_date_written", "author"]
        exclude = ["desc", "view", "edit", "noduplicate", "delete"]

    author = tables.Column(
        verbose_name="Author", accessor="author_name", orderable=True
    )

    def render_availability(self, value):
        symbol = "indeterminate_question_box"
        if value == "lost":
            symbol = "close"
        elif value == "non-accessible":
            symbol = "lock"
        elif value == "available":
            symbol = "check"
        return mark_safe(f'<span class="material-symbols-outlined">{symbol}</span>')

    def render_author(self, record):
        context = {
            "entity_id": record.author_id,
            "entity_name": record.author_name,
            "entity_uri": f"/apis/apis_ontology.person/{record.author_id}",  # TODO: use urls
        }
        return mark_safe(
            render_to_string("apis_ontology/linked_entity_column.html", context)
        )


class TibScholRelationMixinTable(GenericTable):
    class Meta(GenericTable.Meta):
        fields = [
            "subj",
            "obj",
            "edit",
            "delete",
        ]
        exclude = ["view", "desc"]

    def render_support_notes(self, record):
        notes = parse_comment(render_list_field(record.support_notes))
        preview = parse_comment(
            render_list_field(preview_text(record.support_notes, 50))
        )
        context = {
            "record": record,
            "preview_value": mark_safe(preview),
            "field_value": mark_safe(notes),
            "field_name": "support_notes",
        }

        return mark_safe(render_to_string("apis_ontology/preview_column.html", context))

    def render_zotero_refs(self, record):
        zotero_refs = mark_safe(parse_comment(render_list_field(record.zotero_refs)))
        preview = mark_safe(
            parse_comment(render_list_field(preview_text(record.zotero_refs, 50)))
        )
        context = {
            "record": record,
            "preview_value": preview,
            "field_value": zotero_refs,
            "field_name": "zotero_refs",
        }
        return mark_safe(render_to_string("apis_ontology/preview_column.html", context))

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

    def render_obj(self, record):
        actual_obj = RootObject.objects_inheritance.get_subclass(pk=record.obj.pk)

        return mark_safe(
            "<a href='"
            + actual_obj.get_absolute_url()
            + "' target='_BLANK'>"
            + str(actual_obj)
            + "</a>"
        )

    def render_subj(self, record):
        actual_obj = RootObject.objects_inheritance.get_subclass(pk=record.subj.pk)

        return mark_safe(
            "<a href='"
            + actual_obj.get_absolute_url()
            + "' target='_BLANK'>"
            + str(actual_obj)
            + "</a>"
        )


class RelationsTable(TibScholRelationMixinTable):
    reverse = False

    name = tables.Column(verbose_name="Relationship", orderable=False)
    obj = tables.Column(verbose_name="Object", orderable=False)
    support_notes = tables.Column(orderable=False)
    zotero_refs = tables.Column(verbose_name="Zotero", orderable=False)
    tei_refs = tables.Column(verbose_name="Excerpts", orderable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the obj attribute based on the value of self.reverse
        xslt_file = "apis_ontology/xslt/teibp.xsl"
        xslt = etree.parse(xslt_file)
        self.transform = etree.XSLT(xslt)

    def render_name(self, record):
        rel_name = record.name
        try:
            if self.context["object"].pk == record.obj.pk:
                rel_name = record.reverse_name
        except Exception as e:
            logger.error("Bad relation %s\Error: %s", record, repr(e))

        return rel_name

    def render_obj(self, record):
        # return str(record) + str(self.context["object"].pk)
        actual_obj = RootObject.objects_inheritance.get_subclass(pk=record.obj.pk)

        try:
            if self.context["object"].pk == record.obj.pk:
                # return str(RootObject.objects_inheritance.get_subclass(pk=record.subj.pk))
                actual_obj = RootObject.objects_inheritance.get_subclass(
                    pk=record.subj.pk
                )
        except Exception as e:
            logger.error("Bad relation %s\Error: %s", record, repr(e))

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
        "<a href='{% url 'apis:relationupdate' record.id %}' target=\"_BLANK\"><span class=\"material-symbols-outlined\">edit</span></a>",
        orderable=False,
        verbose_name="",
        attrs={"td": {"style": "max-width: 2em"}},
    )

    delete = tables.TemplateColumn(
        "<a href='{% url 'apis:relationdelete' record.id %}?next={{ request.GET.next }}' target=\"_BLANK\"><span class=\"material-symbols-outlined\">delete</span></a>",
        orderable=False,
        verbose_name="",
        attrs={"td": {"style": "max-width: 2em"}},
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


class WorkCommentaryOnWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = [
            "subj",
            "obj",
            "commentary_author",
            "edit",
            "delete",
        ]

    subj = tables.Column()
    obj = tables.Column()
    commentary_author = tables.Column(
        verbose_name="Author (obj)", orderable=False, accessor="obj"
    )

    def render_commentary_author(self, value):
        obj_work = Work.objects.get(pk=value.pk)
        if obj_work.author_id:
            return f"{obj_work.author_name} ({obj_work.author_id})"
        return ""


class WorkComposedAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = [
            "subj",
            "obj",
            "work_author",
            "edit",
            "delete",
        ]

    subj = tables.Column(verbose_name="Work")
    work_author = tables.Column(verbose_name="Author", orderable=False, accessor="subj")
    obj = tables.Column(verbose_name="Place")

    def render_work_author(self, value):
        work = Work.objects.get(pk=value.pk)
        if work.author_id:
            return f"{work.author_name} ({work.author_id})"
        return ""
