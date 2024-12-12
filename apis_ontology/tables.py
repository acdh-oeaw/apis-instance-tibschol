import logging

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.generic.tables import CustomTemplateColumn, GenericTable, MoreLessColumn
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import format_html

import re

from .models import Instance, Person, Place, Work
from .templatetags.filter_utils import (
    render_coordinate,
    render_links,
    render_list_field,
)
from .templatetags.parse_comment import parse_comment

logger = logging.getLogger(__name__)


def preview_text(text, n=50):
    if not text:
        return ""
    if len(text) <= n:
        return text
    truncated_text = text[:n].rsplit(" ", 1)[0]
    return truncated_text + "…"


class TibscholEntityMixinTable(AbstractEntityTable):
    paginate_by = 100

    def render_alternative_names(self, value):
        return render_list_field(value)

    def render_external_links(self, value):
        return render_links(value)

    def render_comments(self, value):
        return mark_safe(parse_comment(value))

    name = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_name(self, record):
        return str(record)


class PlaceTable(TibscholEntityMixinTable):
    class Meta:
        model = Place
        fields = ["label", "longitude", "latitude"]
        exclude = ["name", "desc", "view", "edit", "noduplicate", "delete"]

    label = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_label(self, record):
        return str(record)

    def render_latitude(self, value):
        return render_coordinate(value)

    def render_longitude(self, value):
        return render_coordinate(value)


class PersonTable(TibscholEntityMixinTable):
    class Meta:
        model = Person
        fields = ["name"]
        exclude = ["id", "desc", "view", "edit", "noduplicate", "delete"]

    def render_name(self, record):
        return str(record)


class WorkTable(TibscholEntityMixinTable):
    class Meta:
        model = Work
        fields = ["name", "author"]
        exclude = ["id", "desc", "view", "edit", "noduplicate", "delete"]
        row_attrs = {
            "style": lambda record: (
                "background-color: lightgray;" if not record.isExtant else None
            )
        }

    author = tables.Column(
        verbose_name="Author", accessor="author_name", orderable=True
    )

    def render_author(self, record):
        context = {
            "entity_id": record.author_id,
            "entity_name": record.author_name,
            "entity_uri": Person.objects.get(pk=record.author_id).uri,
        }
        return mark_safe(
            render_to_string("apis_ontology/linked_entity_column.html", context)
        )


class InstanceTable(TibscholEntityMixinTable):
    class Meta:
        model = Instance
        fields = ["name", "start_date_written", "author"]
        exclude = ["id", "desc", "view", "edit", "noduplicate", "delete"]

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
            "entity_uri": Person.objects.get(pk=record.author_id).uri,
        }
        return mark_safe(
            render_to_string("apis_ontology/linked_entity_column.html", context)
        )


class TibScholRelationColumn(tables.Column):
    template_name = None
    orderable = False
    exclude_from_export = False
    verbose_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            orderable=self.orderable,
            exclude_from_export=self.exclude_from_export,
            verbose_name=self.verbose_name,
            *args,
            **kwargs,
        )


class RelationNameColumn(CustomTemplateColumn):
    template_name = "columns/relation_name.html"
    verbose_name = "Relation"
    orderable = False


class RelationPredicateColumn(CustomTemplateColumn):
    template_name = "columns/relation_predicate.html"
    verbose_name = "Object"
    orderable = False

    def render(self, record, **kwargs):
        # Check if `record.subj` has `isExtant` and if it's False
        predicate = record.obj if record.forward else record.subj
        highlight_style = (
            "background-color: lightgray;"
            if hasattr(predicate, "isExtant") and not predicate.isExtant
            else ""
        )
        # Render the template with the additional context
        self.extra_context["highlight_style"] = highlight_style
        # Render template with updated context
        return super().render(record, **kwargs)


class TEIRefColumn(TibScholRelationColumn):
    verbose_name = "TEI REfs"

    def render(self, record, *args, **kwargs):
        def linkify_excerpt_id(xml_id):
            true_id = xml_id.replace('"', "").replace("xml:id=", "").strip().rstrip(".")
            return f"""<a href="#" onclick="showPopup('{true_id}'); return false;">
            {true_id}
            </a>"""

        value = record.tei_refs
        lines = value.split("\n")
        linked_lines = []
        for l in lines:
            words = l.split()
            linked_words = []
            for w in words:
                if w.startswith("xml:id=") or bool(re.search(r"\bex\d\w*", w)):
                    linked_words.append(linkify_excerpt_id(w))
                else:
                    linked_words.append(w)
            linked_lines.append(" ".join(linked_words))

        return mark_safe("<br />".join(linked_lines))


class TibScholEntityMixinRelationsTable(GenericTable):
    relation = RelationNameColumn()
    predicate = RelationPredicateColumn()
    support_notes = MoreLessColumn(
        orderable=False,
        preview=lambda x: mark_safe(
            parse_comment(render_list_field(preview_text(x.support_notes, 50)))
        ),
        fulltext=lambda x: mark_safe(parse_comment(render_list_field(x.support_notes))),
    )
    zotero_refs = MoreLessColumn(
        orderable=False,
        preview=lambda x: mark_safe(
            parse_comment(render_list_field(preview_text(x.zotero_refs, 50)))
        ),
        fulltext=lambda x: mark_safe(parse_comment(render_list_field(x.zotero_refs))),
    )
    tei_refs = TEIRefColumn()

    class Meta(GenericTable.Meta):
        fields = [
            "support_notes",
            "zotero_refs",
            "tei_refs",
        ]
        exclude = ["desc"]
        per_page = 1000


class TibScholRelationMixinTable(GenericTable):
    paginate_by = 100

    class Meta(GenericTable.Meta):
        fields = ["subj", "obj"]
        exclude = ["desc"]

    def render_subj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def render_obj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)


class WorkCommentaryOnWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = [
            "subj",
            "obj",
            "commentary_author",
        ]
        sequence = ("subj", "obj", "commentary_author", "...")

    commentary_author = tables.Column(
        verbose_name="Author (obj)", orderable=False, accessor="obj"
    )

    def render_commentary_author(self, value):
        obj_work = Work.objects.get(pk=value.pk)
        if obj_work.author_id:
            author = Person.objects.get(pk=obj_work.author_id)
            return format_html(
                '<a href="{}" target="_blank">{}</a>', author.get_absolute_url(), author
            )
        return ""


# class WorkComposedAtPlaceTable(TibScholRelationMixinTable):
#     class Meta(TibScholRelationMixinTable.Meta):
#         fields = [
#             "subj",
#             "obj",
#             "work_author",
#             "edit",
#             "delete",
#         ]

#     subj = tables.Column(verbose_name="Work")
#     work_author = tables.Column(verbose_name="Author", orderable=False, accessor="subj")
#     obj = tables.Column(verbose_name="Place")

#     def render_work_author(self, value):
#         work = Work.objects.get(pk=value.pk)
#         if work.author_id:
#             return f"{work.author_name} ({work.author_id})"
#         return ""


# class PersonActiveAtPlaceTable(TibScholRelationMixinTable):
#     class Meta(TibScholRelationMixinTable.Meta):
#         fields = [
#             "subj",
#             "obj",
#             "author_dates",
#             "edit",
#             "delete",
#         ]

#     subj = tables.Column(verbose_name="Person")
#     author_dates = tables.Column(
#         verbose_name="Lifespan", orderable=False, accessor="subj"
#     )
#     obj = tables.Column(verbose_name="Place")

#     def render_author_dates(self, value):
#         author = Person.objects.get(pk=value.pk)
#         return (
#             (author.start_date_written if author.start_date_written else "")
#             + " - "
#             + (author.end_date_written if author.end_date_written else "")
#         )
