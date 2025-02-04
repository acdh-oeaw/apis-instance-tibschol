import logging

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.generic.tables import CustomTemplateColumn, GenericTable, MoreLessColumn
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import re
from django.db.models import OuterRef, Subquery
from django.db.models import Value
from django.db.models.functions import Coalesce

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


class AuthorColumn(tables.Column):
    def render(self, value, *args, **kwargs):
        try:
            subj_work = Work.objects.get(pk=value)
        except Work.DoesNotExist:
            subj_work = Instance.objects.get(pk=value)

        if subj_work.author_id:
            author = Person.objects.get(pk=subj_work.author_id)
            context = {
                "entity_id": author.id,
                "entity_name": author.name,
                "entity_uri": author.get_absolute_url(),
            }
            return mark_safe(
                render_to_string("apis_ontology/linked_entity_column.html", context)
            )

        return ""

    def order(self, queryset, is_descending):
        queryset = queryset.annotate(
            author_str=Coalesce(
                Subquery(
                    Work.objects.filter(pk=OuterRef(self.accessor)).values(
                        "author_name"
                    )[:1]
                ),
                Subquery(
                    Instance.objects.filter(pk=OuterRef(self.accessor)).values(
                        "author_name"
                    )[:1]
                ),
                Value(""),
            )
        ).order_by(("-" if is_descending else "") + "author_str")
        return queryset, True


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

    author = AuthorColumn(verbose_name="Author", accessor="id", orderable=True)


class InstanceTable(TibscholEntityMixinTable):
    class Meta:
        model = Instance
        fields = ["name", "start_date_written", "author"]
        exclude = ["id", "desc", "view", "edit", "noduplicate", "delete"]

    author = AuthorColumn(verbose_name="Author", accessor="id", orderable=True)

    def render_availability(self, value):
        symbol = "indeterminate_question_box"
        if value == "lost":
            symbol = "close"
        elif value == "non-accessible":
            symbol = "lock"
        elif value == "available":
            symbol = "check"
        return mark_safe(f'<span class="material-symbols-outlined">{symbol}</span>')

    author = AuthorColumn(verbose_name="Author", accessor="work_id", orderable=True)


class TibScholRelationColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(
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
                if (
                    w.startswith("xml:id=")
                    or bool(re.search(r"\bex(?:\d\w*)\b", w))
                    or bool(re.search(r"\bexX(?:\w*)\b", w))
                ):
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
    tei_refs = TEIRefColumn(verbose_name="TEI Refs", orderable=False)

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
        exclude = ["desc", "view", "edit", "delete"]
        sequence = ("subj", "obj", "...")

    subj = tables.Column(verbose_name="Subject")
    obj = tables.Column(verbose_name="Object")

    def render_subj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def render_obj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def order_subj(self, queryset, is_descending):
        queryset = queryset.annotate(
            subj_str=Subquery(
                Person.objects.filter(pk=OuterRef("subj_object_id"))
                .values("name")[:1]
                .union(
                    Place.objects.filter(pk=OuterRef("subj_object_id")).values("label")[
                        :1
                    ]
                )
                .union(
                    Work.objects.filter(pk=OuterRef("subj_object_id")).values("name")[
                        :1
                    ]
                )
                .union(
                    Instance.objects.filter(pk=OuterRef("subj_object_id")).values(
                        "name"
                    )[:1]
                ),
            ),
        ).order_by(("-" if is_descending else "") + "subj_str")
        return queryset, True

    def order_obj(self, queryset, is_descending):
        queryset = queryset.annotate(
            obj_str=Subquery(
                Person.objects.filter(pk=OuterRef("obj_object_id"))
                .values("name")[:1]
                .union(
                    Place.objects.filter(pk=OuterRef("obj_object_id")).values("label")[
                        :1
                    ]
                )
                .union(
                    Work.objects.filter(pk=OuterRef("obj_object_id")).values("name")[:1]
                )
                .union(
                    Instance.objects.filter(pk=OuterRef("obj_object_id")).values(
                        "name"
                    )[:1]
                ),
            ),
        ).order_by(("-" if is_descending else "") + "obj_str")

        return queryset, True


class WorkCommentaryOnWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "commentary_author", "obj", "work_author"]
        sequence = ("subj", "commentary_author", "obj", "work_author", "...")

    work_author = AuthorColumn(
        verbose_name="Author (obj)", orderable=True, accessor="obj_object_id"
    )
    commentary_author = AuthorColumn(
        verbose_name="Author (subj)", orderable=True, accessor="subj_object_id"
    )


class WorkComposedAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = [
            "subj",
            "work_author",
            "obj",
        ]
        sequence = ("subj", "work_author", "obj", "...")

    work_author = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class PersonActiveAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "lifespan"]
        sequence = ("subj", "obj", "lifespan", "...")

    lifespan = tables.Column(verbose_name="Lifespan", orderable=True, accessor="subj")

    def order_lifespan(self, queryset, is_descending):
        queryset = queryset.annotate(
            person_start=Subquery(
                Person.objects.filter(pk=OuterRef("subj_object_id")).values(
                    "start_date"
                )[:1]
            ),
            person_end=Subquery(
                Person.objects.filter(pk=OuterRef("subj_object_id")).values("end_date")[
                    :1
                ]
            ),
        )
        order = (
            ("-" if is_descending else "") + "person_start",
            ("-" if is_descending else "") + "person_end",
        )

        queryset = queryset.order_by(*order)
        return queryset, True

    def render_lifespan(self, value):
        author = Person.objects.get(pk=value.pk)
        return (
            (author.start_date_written if author.start_date_written else "")
            + " - "
            + (author.end_date_written if author.end_date_written else "")
        )


class PersonAddresseeOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "work_author"]
        sequence = ("subj", "obj", "work_author", "...")

    work_author = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonBiographedInWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "work_author"]
        sequence = ("subj", "obj", "work_author", "...")

    work_author = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class WorkContainsCitationsOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_subj", "author_obj"]
        sequence = ("subj", "author_subj", "obj", "author_obj", "...")

    author_subj = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )
    author_obj = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class InstanceWrittenAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class WorkHasAsAnInstanceInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class InstanceIsCopiedFromInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )
