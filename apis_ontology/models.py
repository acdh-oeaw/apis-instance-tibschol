import logging

from apis_core.apis_entities.abc import E53_Place
from apis_core.apis_entities.models import AbstractEntity
from apis_core.core.models import LegacyDateMixin
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
from apis_core.apis_metainfo.models import RootObject
from apis_core.utils.helpers import create_object_from_uri
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import OuterRef, QuerySet, Subquery
from django.db.models.signals import class_prepared
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from crum import get_current_user

logger = logging.getLogger(__name__)


class Subject(GenericModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ["name"]


class TibScholEntityMixin(models.Model):
    class Meta:
        abstract = True

    comments = models.TextField(blank=True, null=True)
    alternative_names = models.TextField(
        blank=True, null=True, verbose_name="Alternative names"
    )
    external_links = models.TextField(
        blank=True, null=True, verbose_name="External links"
    )


class LegacyStuffMixin(models.Model):
    class Meta:
        abstract = True

    review = models.BooleanField(
        default=False,
        help_text="Should be set to True, if the "
        "data record holds up quality "
        "standards.",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    # published = models.BooleanField(default=False)
    published = None

    @classmethod
    def get_or_create_uri(cls, uri):
        logger.info(f"using custom get_or_create_uri with %s", uri)
        return create_object_from_uri(uri, cls) or cls.objects.get(pk=uri)

    @property
    def uri(self):
        contenttype = ContentType.objects.get_for_model(self)
        uri = reverse("apis_core:generic:detail", args=[contenttype, self.pk])
        return uri


class TibScholEntityManager(models.Manager):
    def get_queryset(self):
        user = get_current_user()
        if user and user.is_authenticated:
            return super().get_queryset()

        return super().get_queryset().filter(review=True)


class Person(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"

    start_date_written = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Life date start",
    )
    end_date_written = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Life date end",
    )

    GENDERS = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    NATIONALITY = [("Indic", "Indic"), ("Tibetan", "Tibetan")]

    name = models.CharField(max_length=255, blank=True, default="", verbose_name="Name")
    gender = models.CharField(max_length=6, choices=GENDERS, default="male")
    nationality = models.CharField(
        max_length=10, choices=NATIONALITY, blank=True, null=True
    )

    objects = TibScholEntityManager()

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("Persons")
        ordering = ["name", "pk"]

    def __str__(self):
        return f"{self.name} ({self.pk})"


class Place(
    E53_Place,
    VersionMixin,
    LegacyStuffMixin,
    LegacyDateMixin,
    TibScholEntityMixin,
    AbstractEntity,
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"
    label = models.CharField(blank=True, default="", verbose_name="Name")
    end_date = None
    end_start_date = None
    end_end_date = None
    end_date_written = None
    start_date_written = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Date",
    )

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("Places")

    def __str__(self):
        return f"{self.label} ({self.pk})"

    objects = TibScholEntityManager()


class WorkQuerySet(QuerySet):
    def with_author(self):
        return self.annotate(
            # Subquery to get the Person ID related to the Work through PersonAuthorOfWork
            author_id=Subquery(
                PersonAuthorOfWork.objects.filter(obj_object_id=OuterRef("id")).values(
                    "subj_object_id"
                )[:1]
            ),
            # Subquery to get the Person's name based on the person_id from above
            author_name=Subquery(
                Person.objects.filter(id=OuterRef("author_id")).values("name")[:1]
            ),
        )


class WorkManager(TibScholEntityManager):
    def get_queryset(self):
        return (
            WorkQuerySet(self.model, using=self._db)
            .filter(id__in=super().get_queryset().values_list("id", flat=True))
            .with_author()
        )


class Work(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"
    end_date = None
    end_start_date = None
    end_end_date = None
    end_date_written = None
    start_date_written = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Date of composition",
    )

    LANGUAGES = [
        ("Sanskrit", "Sanskrit"),
        ("Tibetan", "Tibetan"),
        ("Tangut", "Tangut"),
        ("Other", "Other"),
    ]

    subject_vocab = models.ManyToManyField(Subject, verbose_name="Topic", blank=True)
    name = models.CharField(max_length=255, blank=True, default="", verbose_name="Name")
    sde_dge_ref = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="Derge reference"
    )
    original_language = models.CharField(
        max_length=10, choices=LANGUAGES, blank=True, null=True
    )
    isExtant = models.BooleanField(
        default=True, verbose_name="Is extant", null=True, blank=True
    )

    class Meta:
        verbose_name = _("work")
        verbose_name_plural = _("Works")
        ordering = ["name", "pk"]

    def __str__(self):
        return f"{self.name} ({self.pk})"

    objects = WorkManager()


class InstanceQuerySet(QuerySet):
    def with_author(self):
        return self.annotate(
            # Subquery to get the Person ID related to the Work through PersonAuthorOfWork
            work_id=Subquery(
                WorkHasAsAnInstanceInstance.objects.filter(
                    obj_object_id=OuterRef("id")
                ).values("subj_object_id")[:1]
            ),
            author_id=Subquery(
                PersonAuthorOfWork.objects.filter(
                    obj_object_id=OuterRef("work_id")
                ).values("subj_object_id")[:1]
            ),
            # Subquery to get the Person's name based on the person_id from above
            author_name=Subquery(
                Person.objects.filter(id=OuterRef("author_id")).values("name")[:1]
            ),
        )


class InstanceManager(TibScholEntityManager):
    def get_queryset(self):
        return (
            InstanceQuerySet(self.model, using=self._db)
            .filter(id__in=super().get_queryset().values_list("id", flat=True))
            .with_author()
        )


class Instance(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"
    end_date = None
    end_start_date = None
    end_end_date = None
    end_date_written = None
    start_date_written = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Date",
    )

    SETS = [
        ("Set 1", "Set 1"),
        ("Set 2", "Set 2"),
        ("Set 3", "Set 3"),
        ("Set 4", "Set 4"),
    ]
    AVAILABILITY = [
        ("lost", "lost"),
        ("available", "available"),
        ("non-accessible", "non-accessible"),
    ]
    name = models.CharField(max_length=255, blank=True, default="", verbose_name="Name")
    set_num = models.CharField(
        max_length=5, choices=SETS, null=True, blank=True, verbose_name="Set"
    )
    volume = models.CharField(max_length=255, blank=True, null=True)
    sb_text_number = models.TextField(
        blank=True,
        null=True,
        verbose_name="Number ascribed to item by Tibschol",
    )
    pp_kdsb = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Page numbers in print",
    )
    num_folios = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Number of folios"
    )

    signature_letter = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Signature letter (category)",
    )
    signature_number = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Signature number"
    )
    drepung_number = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Drepung catalogue number"
    )
    provenance = models.TextField(blank=True, null=True, verbose_name="Provenance")
    zotero_ref = models.TextField(blank=True, null=True, verbose_name="Zotero")
    tibschol_ref = models.TextField(
        blank=True, null=True, verbose_name="Tibschol reference"
    )
    availability = models.CharField(
        max_length=15,
        choices=AVAILABILITY,
        blank=True,
        null=True,
        verbose_name="Availability",
    )
    dimension = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="WxH size in cm"
    )
    item_description = models.TextField(
        blank=True, null=True, verbose_name="Item description"
    )

    class Meta:
        verbose_name = _("instance")
        verbose_name_plural = _("Instances")
        ordering = ["name", "pk"]

    def __str__(self):
        return f"{self.name} ({self.pk})"

    objects = InstanceManager()


class ZoteroEntry(GenericModel, models.Model):
    zoteroId = models.CharField(max_length=255, verbose_name="Zotero ID")
    shortTitle = models.TextField(blank=True, null=True, verbose_name="Short title")
    fullCitation = models.TextField(blank=True, null=True, verbose_name="Full Citation")
    year = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Year of publication"
    )


class Excerpts(GenericModel, models.Model):
    xml_id = models.CharField(max_length=255, unique=True)
    xml_content = models.TextField()
    source = models.CharField(max_length=255)  # the TEI file source


#######################################################################################
###################################RELATIONS###########################################
#######################################################################################


class TibScholRelationMixin(VersionMixin, Relation, LegacyDateMixin, GenericModel):
    CONFIDENCE = [
        ("Positive", "Positive"),
        ("Uncertain", "Uncertain"),
        ("Negative", "Negative"),
    ]

    zotero_refs = models.TextField(blank=True, null=True, verbose_name="Zotero")
    tei_refs = models.TextField(blank=True, null=True, verbose_name="Excerpts")
    support_notes = models.TextField(
        blank=True, null=True, verbose_name="Support notes"
    )
    confidence = models.CharField(
        blank=True,
        null=True,
        default="Positive",
        choices=CONFIDENCE,
        verbose_name="Confidence",
        max_length=1000,
    )
    subj_model = None
    obj_model = None

    @property
    def subject_type(self):
        return str(self.subj_model.__name__).lower()

    @property
    def object_type(self):
        return str(self.obj_model.__name__).lower()

    class Meta:
        abstract = True


def enforce_meta_attributes(sender, **kwargs):
    if issubclass(sender, TibScholRelationMixin):
        meta = sender._meta
        # set verbose_name_plural to verbose_name
        meta.verbose_name_plural = meta.verbose_name or sender.__name__.lower()
        meta.ordering = ["subj_object_id", "obj_object_id"]


class_prepared.connect(enforce_meta_attributes)


class PersonActiveAtPlace(TibScholRelationMixin):
    subj_model = Person
    obj_model = Place
    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )

    @classmethod
    def name(cls) -> str:
        return "active at"

    @classmethod
    def reverse_name(cls) -> str:
        return "place of activity of"


class PersonAddresseeOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "addressee of"

    @classmethod
    def reverse_name(cls) -> str:
        return "addressed to"


class PersonAuthorOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "author of"

    @classmethod
    def reverse_name(cls) -> str:
        return "composed by"


class PersonBiographedInWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "biographed in"

    @classmethod
    def reverse_name(cls) -> str:
        return "biography of"


class PersonBiographerOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "biographer of"

    @classmethod
    def reverse_name(cls) -> str:
        return "biographed by"


class WorkCommentaryOnWork(TibScholRelationMixin):
    subj_model = Work
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "commentary on"

    @classmethod
    def reverse_name(cls) -> str:
        return "has as a commentary"


class WorkComposedAtPlace(TibScholRelationMixin):
    subj_model = Work
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "composed at"

    @classmethod
    def reverse_name(cls) -> str:
        return "place of composition for"


class WorkContainsCitationsOfWork(TibScholRelationMixin):
    subj_model = Work
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "contains citations of"

    @classmethod
    def reverse_name(cls) -> str:
        return "is cited in"


class InstanceWrittenAtPlace(TibScholRelationMixin):
    subj_model = Instance
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "written at"

    @classmethod
    def reverse_name(cls) -> str:
        return "place of scribing for"


class PersonLineagePredecessorOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "lineage predecessor of"

    @classmethod
    def reverse_name(cls) -> str:
        return "lineage successor of"

    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )


class WorkHasAsAnInstanceInstance(TibScholRelationMixin):
    subj_model = Work
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "has as an instance"

    @classmethod
    def reverse_name(cls) -> str:
        return "instance of"


class PersonOtherRelationToPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "other relation to"

    @classmethod
    def reverse_name(cls) -> str:
        return "other relation to"


class InstanceIsCopiedFromInstance(TibScholRelationMixin):
    subj_model = Instance
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "has source"

    @classmethod
    def reverse_name(cls) -> str:
        return "is source for"

    class Meta:
        verbose_name = "instance has source"


class PlaceLocatedWithinPlace(TibScholRelationMixin):
    subj_model = Place
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "located within"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class PersonOrdinatorOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "ordinator of"

    @classmethod
    def reverse_name(cls) -> str:
        return "ordained by"


class PersonOwnerOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "owner of"

    @classmethod
    def reverse_name(cls) -> str:
        return "owned by"


class PersonParentOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "parent of"

    @classmethod
    def reverse_name(cls) -> str:
        return "child of"


class PersonPrompterOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "prompter of"

    @classmethod
    def reverse_name(cls) -> str:
        return "prompted by"


class WorkRecordsTheTeachingOfPerson(TibScholRelationMixin):
    subj_model = Work
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "records the teaching of"

    @classmethod
    def reverse_name(cls) -> str:
        return "has their teaching recorded in"


class PersonQuotesWithNamePerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "quotes with name"

    @classmethod
    def reverse_name(cls) -> str:
        return "is quoted with name by"

    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )


class PersonQuotesWithoutNamePerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "quotes without name"

    @classmethod
    def reverse_name(cls) -> str:
        return "is quoted without name by"

    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )


class PersonRequestsPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "requests"

    @classmethod
    def reverse_name(cls) -> str:
        return "requested by"

    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )


class PersonScribeOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "scribe of"

    @classmethod
    def reverse_name(cls) -> str:
        return "copied/written down by"


class PersonSiblingOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "sibling of"

    @classmethod
    def reverse_name(cls) -> str:
        return "sibling of"


class PersonSponsorOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "sponsor of"

    @classmethod
    def reverse_name(cls) -> str:
        return "sponsored by"


class PersonStudentOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "student of"

    @classmethod
    def reverse_name(cls) -> str:
        return "teacher of"

    subject_of_teaching_vocab = models.ManyToManyField(
        Subject, verbose_name="Topic of teaching", blank=True
    )


class PersonStudiesWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "studies"

    @classmethod
    def reverse_name(cls) -> str:
        return "studied by"


class PersonTeachesWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "teaches"

    @classmethod
    def reverse_name(cls) -> str:
        return "taught by"


class PersonUncleMaternalPaternalOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "uncle (maternal/paternal) of"

    @classmethod
    def reverse_name(cls) -> str:
        return "nephew (maternal/paternal) of"


class WorkTaughtAtPlace(TibScholRelationMixin):
    subj_model = Work
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "taught at"

    @classmethod
    def reverse_name(cls) -> str:
        return "place of teaching of"


class PersonTranslatorOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "translator of"

    @classmethod
    def reverse_name(cls) -> str:
        return "translated by"


class PersonHasOtherRelationWithInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance

    @classmethod
    def name(cls) -> str:
        return "has other relation with"

    @classmethod
    def reverse_name(cls) -> str:
        return "has other relation with"
