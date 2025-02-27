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
from .templatetags.render_tei_refs import render_tei_refs

from datetime import datetime

logger = logging.getLogger(__name__)


def preview_text(text, n=50):
    if not text:
        return ""
    if len(text) <= n:
        return text
    truncated_text = text[:n].rsplit(" ", 1)[0]
    return truncated_text + "…"


class TibscholEntityMixinTable(AbstractEntityTable):
    class Meta(AbstractEntityTable.Meta):
        exclude = ["id", "desc", "view", "edit", "delete", "noduplicate"]
        sequence = (
            "name",
            "...",
        )

    export_filename = f"tibschol_export_{datetime.now().strftime('%Y%m%d_%H%M')}"

    export_alternative_names = tables.Column(
        visible=False, verbose_name="Alternative names", accessor="alternative_names"
    )
    export_external_links = tables.Column(
        visible=False, verbose_name="External links", accessor="external_links"
    )
    export_comments = tables.Column(
        visible=False, verbose_name="Comments", accessor="comments"
    )
    export_review = tables.Column(
        visible=False, verbose_name="Review", accessor="review"
    )
    export_notes = tables.Column(visible=False, verbose_name="Notes", accessor="notes")

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

    def value_name(self, record):
        return getattr(record, "label", getattr(record, "name", ""))


class PersonDateColumn(tables.Column):
    def render(self, value, *args, **kwargs):
        try:
            person = Person.objects.get(pk=value)
        except Person.DoesNotExist:
            return ""
        return (
            (person.start_date_written if person.start_date_written else "")
            + " - "
            + (person.end_date_written if person.end_date_written else "")
        )

    def order(self, queryset, is_descending):
        queryset = queryset.annotate(
            person_start=Subquery(
                Person.objects.filter(pk=OuterRef(self.accessor)).values("start_date")[
                    :1
                ]
            ),
            person_end=Subquery(
                Person.objects.filter(pk=OuterRef(self.accessor)).values("end_date")[:1]
            ),
        ).order_by(
            ("-" if is_descending else "") + "person_start",
            ("-" if is_descending else "") + "person_end",
        )
        return queryset, True


class AuthorColumn(tables.Column):
    def get_work_from_id(self, work_instance_id):
        try:
            return Work.objects.get(pk=work_instance_id)
        except Work.DoesNotExist:
            # if the _object_id is not a work, look for an instance
            try:
                return Instance.objects.get(pk=work_instance_id)
            except Instance.DoesNotExist:
                logger.warn(
                    "Unable to find work or instance for %s: %s",
                    self.accessor,
                    work_instance_id,
                )

    def render(self, value, *args, **kwargs):
        subj_work = self.get_work_from_id(value)
        if not subj_work:
            return ""
        if getattr(subj_work, "author_id"):
            try:
                author = Person.objects.get(pk=getattr(subj_work, "author_id"))
                context = {
                    "entity_id": author.pk,
                    "entity_name": author.name,
                    "entity_uri": author.get_absolute_url(),
                }
                return mark_safe(
                    render_to_string("apis_ontology/linked_entity_column.html", context)
                )
            except Person.DoesNotExist:
                # Author is deleted or not accessible to the user
                logger.warning("Unable to find author for %s ", subj_work)

        return ""

    def value(self, value, *args, **kwargs):
        work = self.get_work_from_id(value)
        if not work:
            return ""
        return getattr(work, "author_name", "")

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
    class Meta(TibscholEntityMixinTable.Meta):
        model = Place
        fields = ["name", "longitude", "latitude"]
        sequence = (
            "name",
            "longitude",
            "latitude",
            "...",
        )

    export_date = tables.Column(
        verbose_name="Date", accessor="start_date_written", visible=False
    )

    def render_latitude(self, value):
        return render_coordinate(value)

    def render_longitude(self, value):
        return render_coordinate(value)


class PersonTable(TibscholEntityMixinTable):
    class Meta(TibscholEntityMixinTable.Meta):
        model = Person
        fields = ["name"]
        # exclude = ["id", "desc", "view", "edit", "noduplicate", "delete"]

    def render_name(self, record):
        return str(record)

    export_lifedate_start = tables.Column(
        accessor="start_date_written", verbose_name="Life date start", visible=False
    )
    export_lifedate_end = tables.Column(
        accessor="end_date_written", verbose_name="Life date end", visible=False
    )
    export_gender = tables.Column(
        accessor="gender", verbose_name="Gender", visible=False
    )
    export_nationality = tables.Column(
        accessor="nationality", verbose_name="Nationality", visible=False
    )

    def order_start_date_written(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date")
        return queryset, True

    def order_end_date_written(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "end_date")
        return queryset, True


class WorkTable(TibscholEntityMixinTable):
    class Meta(TibscholEntityMixinTable.Meta):
        model = Work
        fields = ["name", "author"]
        row_attrs = {
            "style": lambda record: (
                "background-color: lightgray;" if not record.isExtant else None
            )
        }

    author = AuthorColumn(verbose_name="Author", accessor="id", orderable=True)
    export_date_of_composition = tables.Column(
        accessor="start_date_written", verbose_name="Date of composition", visible=False
    )
    export_topic = tables.Column(
        accessor="subject_vocab", verbose_name="Topic", visible=False
    )

    def value_export_topic(self, record):
        return "\n".join(str(sub) for sub in record.subject_vocab.all())

    def order_start_date_written(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date")
        return queryset, True


class InstanceTable(TibscholEntityMixinTable):
    class Meta(TibscholEntityMixinTable.Meta):
        model = Instance
        fields = ["name", "start_date_written", "author"]

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

    def order_start_date_written(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "start_date")
        return queryset, True

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


class TibScholEntityMixinRelationsTable(GenericTable):
    relation = RelationNameColumn()
    predicate = RelationPredicateColumn()
    references = MoreLessColumn(
        orderable=False,
        preview=lambda x: "",
        fulltext=lambda x: mark_safe(
            render_tei_refs(getattr(x, "tei_refs", "") or "")
            + parse_comment(
                render_list_field(
                    f"{getattr(x,'support_notes', '') or ''}\n{getattr(x, 'zotero_refs','')  or ''}",
                )
            )
        ),
    )

    class Meta(GenericTable.Meta):
        exclude = ["desc"]
        per_page = 1000


class TibScholRelationMixinTable(GenericTable):
    paginate_by = 100
    export_filename = (
        f"tibschol_relation_export_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    class Meta(GenericTable.Meta):
        fields = ["subj", "obj"]
        exclude = ["desc", "view", "edit", "delete"]
        sequence = ("subj", "obj", "...")

    subj = tables.Column(verbose_name="Subject")
    obj = tables.Column(verbose_name="Object")

    def render_subj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def value_subj(self, value):
        return getattr(value, "name", "") or getattr(value, "label", "") or ""

    def render_obj(self, value):
        url = value.get_absolute_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, value)

    def value_obj(self, value):
        return getattr(value, "name", "") or getattr(value, "label", "") or ""

    def render_zotero_refs(self, value):
        return mark_safe(parse_comment(render_list_field(value)))

    def value_zotero_refs(self, value):
        return value

    def render_support_notes(self, value):
        return mark_safe(parse_comment(render_list_field(value)))

    def value_support_notes(self, value):
        return value

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
        sequence = ("subj", "lifespan", "obj", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )


class PersonAddresseeOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "work_author"]
        sequence = ("subj", "lifespan", "obj", "work_author", "...")

    work_author = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )
    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )


class PersonBiographedInWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "work_author"]
        sequence = ("subj", "lifespan", "obj", "work_author", "...")

    work_author = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )
    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )


class PersonBiographerOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class WorkContainsCitationsOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_subj", "author_obj"]
        sequence = ("subj", "author_subj", "obj", "author_obj", "...")

    author_subj = AuthorColumn(
        verbose_name="Author (subj)", orderable=True, accessor="subj_object_id"
    )
    author_obj = AuthorColumn(
        verbose_name="Author (obj)", orderable=True, accessor="obj_object_id"
    )


class InstanceWrittenAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class PersonLineagePredecessorOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class WorkHasAsAnInstanceInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class PersonOtherRelationToPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class InstanceIsCopiedFromInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class PersonOrdinatorOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonOwnerOfInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "lifespan", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonParentOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonPrompterOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class WorkRecordsTheTeachingOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "lifespan", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )
    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="obj_object_id"
    )


class PersonQuotesWithNamePersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonQuotesWithoutNamePersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonRequestsPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonScribeOfInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonSiblingOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonSponsorOfInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonStudentOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class PersonStudiesWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonTeachesWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonUncleMaternalPaternalOfPersonTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj"]
        sequence = ("subj", "lifespan_subj", "obj", "lifespan_obj", "...")

    lifespan_subj = PersonDateColumn(
        verbose_name="Lifespan (subj)", orderable=True, accessor="subj_object_id"
    )
    lifespan_obj = PersonDateColumn(
        verbose_name="Lifespan (obj)", orderable=True, accessor="obj_object_id"
    )


class WorkTaughtAtPlaceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "author_work", "obj", "...")

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="subj_object_id"
    )


class PersonTranslatorOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonHasOtherRelationWithInstanceTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "author_work"]
        sequence = ("subj", "lifespan", "obj", "author_work", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )

    author_work = AuthorColumn(
        verbose_name="Author", orderable=True, accessor="obj_object_id"
    )


class PersonAuthorOfWorkTable(TibScholRelationMixinTable):
    class Meta(TibScholRelationMixinTable.Meta):
        fields = ["subj", "obj", "lifespan"]
        sequence = ("subj", "lifespan", "obj", "...")

    lifespan = PersonDateColumn(
        verbose_name="Lifespan", orderable=True, accessor="subj_object_id"
    )


class ExcerptsTable(GenericTable):
    class Meta(GenericTable.Meta):
        exclude = ["desc", "edit", "delete"]
        fields = ["xml_id", "xml_content"]
        sequence = ["xml_id", "xml_content", "...", "view"]
        per_page = 100

    def render_xml_id(self, value):
        return mark_safe(render_tei_refs(value))

    def value_xml_id(self, value):
        return value


class ZoteroEntryTable(GenericTable):
    class Meta(GenericTable.Meta):
        exclude = ["desc", "view", "edit", "delete"]
        fields = ["zoteroId", "shortTitle", "fullCitation", "year"]
        sequence = fields + ["..."]
        per_page = 100

    zoteroId = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        empty_values=[],
    )

    def render_zoteroId(self, value):
        return value
