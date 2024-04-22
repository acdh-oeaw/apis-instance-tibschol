import logging

logger = logging.getLogger(__name__)

from apis_core.apis_entities.models import AbstractEntity
from apis_core.core.models import LegacyDateMixin
from apis_core.utils.helpers import create_object_from_uri
from django.contrib.contenttypes.models import ContentType
from apis_core.generic.abc import GenericModel
from apis_core.apis_entities.abc import E53_Place
from apis_core.history.models import VersionMixin
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.urls import reverse
from apis_core.relations.models import Relation


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
    published = models.BooleanField(default=False)
    collection = models.ManyToManyField("apis_metainfo.Collection", editable=False)

    @classmethod
    def get_or_create_uri(cls, uri):
        logger.info(f"using custom get_or_create_uri with %s", uri)
        return create_object_from_uri(uri, cls) or cls.objects.get(pk=uri)

    @property
    def uri(self):
        contenttype = ContentType.objects.get_for_model(self)
        uri = reverse("apis_core:generic:detail", args=[contenttype, self.pk])
        return uri


class Person(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Person"
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

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        return f"{self.name}"


class Place(
    E53_Place,
    VersionMixin,
    LegacyStuffMixin,
    LegacyDateMixin,
    TibScholEntityMixin,
    AbstractEntity,
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Place"

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("Places")

    def __str__(self):
        return f"{self.label}"


class Work(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Work"
    LANGUAGES = [
        ("Sanskrit", "Sanskrit"),
        ("Tibetan", "Tibetan"),
        ("Tangut", "Tangut"),
        ("Other", "Other"),
    ]
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="subject",
    )  # should be a controlled vocabulary field

    name = models.CharField(max_length=255, blank=True, default="", verbose_name="Name")
    sde_dge_ref = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="Derge reference"
    )
    original_language = models.CharField(
        max_length=10, choices=LANGUAGES, blank=True, null=True
    )
    isExtant = models.BooleanField(default=True, verbose_name="Is extant")

    class Meta:
        verbose_name = _("work")
        verbose_name_plural = _("Works")

    def __str__(self):
        return f"{self.name}"


class Instance(
    VersionMixin, LegacyStuffMixin, LegacyDateMixin, TibScholEntityMixin, AbstractEntity
):
    class_uri = "http://id.loc.gov/ontologies/bibframe/Instance"
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
    provenance = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Provenance"
    )
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
    item_description = models.TextField(
        blank=True, null=True, verbose_name="Item description"
    )

    class Meta:
        verbose_name = _("instance")
        verbose_name_plural = _("Instances")

    def __str__(self):
        return f"{self.name}"


class ZoteroEntry(GenericModel, models.Model):
    zoteroId = models.CharField(max_length=255, verbose_name="Zotero ID")
    shortTitle = models.TextField(blank=True, null=True, verbose_name="Short title")
    fullCitation = models.TextField(blank=True, null=True, verbose_name="Full Citation")
    year = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Year of publication"
    )


#######################################################################################
###################################RELATIONS###########################################
#######################################################################################


class TibScholRelationMixin(Relation, LegacyDateMixin):
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

    @property
    def subject_type(self):
        return str(self.subj_model.__name__).lower()

    @property
    def object_type(self):
        return str(self.obj_model.__name__).lower()

    class Meta:
        abstract = True


class PersonActiveAtPlace(TibScholRelationMixin):
    subj_model = Person
    obj_model = Place
    name = "active at"
    reverse_name = "place of activity of"
    temptriple_name = "active at"
    temptriple_name_reverse = "place of activity of"


class PersonAddresseeOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "addressee of"
    reverse_name = "addressed to"
    temptriple_name = "addressee of"
    temptriple_name_reverse = "addressed to"


class PersonAuntMaternalPaternalOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "aunt (maternal/paternal) of"
    reverse_name = "nephew (maternal/paternal) of"
    temptriple_name = "aunt (maternal/paternal) of"
    temptriple_name_reverse = "nephew (maternal/paternal) of"


class PersonAuthorOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "author of"
    reverse_name = "composed by"
    temptriple_name = "author of"
    temptriple_name_reverse = "composed by"


class PersonBiographedInWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "biographed in"
    reverse_name = "biography of"
    temptriple_name = "biographed in"
    temptriple_name_reverse = "biography of"


class PersonBiographerOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "biographer of"
    reverse_name = "biographed by"
    temptriple_name = "biographer of"
    temptriple_name_reverse = "biographed by"


class PersonCitesWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "cites"
    reverse_name = "is cited by"
    temptriple_name = "cites"
    temptriple_name_reverse = "is cited by"


class WorkCommentaryOnWork(TibScholRelationMixin):
    subj_model = Work
    obj_model = Work
    name = "commentary on"
    reverse_name = "has as a commentary"
    temptriple_name = "commentary on"
    temptriple_name_reverse = "has as a commentary"


class WorkComposedAtPlace(TibScholRelationMixin):
    subj_model = Work
    obj_model = Place
    name = "composed at"
    reverse_name = "place of composition for"
    temptriple_name = "composed at"
    temptriple_name_reverse = "place of composition for"


class WorkContainsCitationsOfWork(TibScholRelationMixin):
    subj_model = Work
    obj_model = Work
    name = "contains citations of"
    reverse_name = "is cited in"
    temptriple_name = "contains citations of"
    temptriple_name_reverse = "is cited in"


class InstanceCopiedWrittenDownAtPlace(TibScholRelationMixin):
    subj_model = Instance
    obj_model = Place
    name = "copied/written down at"
    reverse_name = "place of scribing for"
    temptriple_name = "copied/written down at"
    temptriple_name_reverse = "place of scribing for"


class PersonDirectPredecessorInLineageOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "direct predecessor (in lineage) of"
    reverse_name = "direct successor (in lineage) of"
    temptriple_name = "direct predecessor (in lineage) of"
    temptriple_name_reverse = "direct successor (in lineage) of"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonDiscipleOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "disciple of"
    reverse_name = "spiritual teacher of"
    temptriple_name = "disciple of"
    temptriple_name_reverse = "spiritual teacher of"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonEditorOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "editor of"
    reverse_name = "edited by"
    temptriple_name = "editor of"
    temptriple_name_reverse = "edited by"


class PersonFellowMonkOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "fellow monk of"
    reverse_name = "fellow monk of"
    temptriple_name = "fellow monk of"
    temptriple_name_reverse = "fellow monk of"


class PersonFellowStudentOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "fellow student of"
    reverse_name = "fellow student of"
    temptriple_name = "fellow student of"
    temptriple_name_reverse = "fellow student of"


class WorkHasAsAnInstanceInstance(TibScholRelationMixin):
    subj_model = Work
    obj_model = Instance
    name = "has as an instance"
    reverse_name = "instance of"
    temptriple_name = "has as an instance"
    temptriple_name_reverse = "instance of"


class PersonHasOtherTypeOfPersonalRelationToPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "has other type of personal relation to"
    reverse_name = "has other type of personal relation to"
    temptriple_name = "has other type of personal relation to"
    temptriple_name_reverse = "has other type of personal relation to"


class PersonIllustratorOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "illustrator of"
    reverse_name = "illustrated by"
    temptriple_name = "illustrator of"
    temptriple_name_reverse = "illustrated by"


class InstanceIsCopiedFromInstance(TibScholRelationMixin):
    subj_model = Instance
    obj_model = Instance
    name = "is copied from"
    reverse_name = "is source for"
    temptriple_name = "is copied from"
    temptriple_name_reverse = "is source for"


class PlaceIsLocatedWithinPlace(TibScholRelationMixin):
    subj_model = Place
    obj_model = Place
    name = "is located within"
    reverse_name = "contains"
    temptriple_name = "is located within"
    temptriple_name_reverse = "contains"


class PersonLenderOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "lender of"
    reverse_name = "lent by"
    temptriple_name = "lender of"
    temptriple_name_reverse = "lent by"


class WorkNamesPerson(TibScholRelationMixin):
    subj_model = Work
    obj_model = Person
    name = "names"
    reverse_name = "is named in"
    temptriple_name = "names"
    temptriple_name_reverse = "is named in"


class WorkNamesWork(TibScholRelationMixin):
    subj_model = Work
    obj_model = Work
    name = "names"
    reverse_name = "is named in"
    temptriple_name = "names"
    temptriple_name_reverse = "is named in"


class PersonOrdinatorOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "ordinator of"
    reverse_name = "ordained by"
    temptriple_name = "ordinator of"
    temptriple_name_reverse = "ordained by"


class PersonOwnerOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "owner of"
    reverse_name = "owned by"
    temptriple_name = "owner of"
    temptriple_name_reverse = "owned by"


class PersonParentOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "parent of"
    reverse_name = "child of"
    temptriple_name = "parent of"
    temptriple_name_reverse = "child of"


class PersonPatronOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "patron of"
    reverse_name = "protegee of"
    temptriple_name = "patron of"
    temptriple_name_reverse = "protegee of"


class PersonPromoterOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "promoter of"
    reverse_name = "promoted by"
    temptriple_name = "promoter of"
    temptriple_name_reverse = "promoted by"


class PersonPrompterOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "prompter of"
    reverse_name = "prompted by"
    temptriple_name = "prompter of"
    temptriple_name_reverse = "prompted by"


class WorkQuotesWithNameTheViewsOfPerson(TibScholRelationMixin):
    subj_model = Work
    obj_model = Person
    name = "quotes (with name) the views of"
    reverse_name = "has views quoted (with name) in"
    temptriple_name = "quotes (with name) the views of"
    temptriple_name_reverse = "has views quoted (with name) in"


class WorkQuotesWithoutNameTheViewsOfPerson(TibScholRelationMixin):
    subj_model = Work
    obj_model = Person
    name = "quotes (without name) the views of"
    reverse_name = "has views quoted (without name) in"
    temptriple_name = "quotes (without name) the views of"
    temptriple_name_reverse = "has views quoted (without name) in"


class WorkRecordsTheTeachingOfPerson(TibScholRelationMixin):
    subj_model = Work
    obj_model = Person
    name = "records the teaching of"
    reverse_name = "has their teaching recorded in"
    temptriple_name = "records the teaching of"
    temptriple_name_reverse = "has their teaching recorded in"


class PersonRefersWithNameToTheViewsOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "refers (with name) to the views of"
    reverse_name = "has views referred to (with name) by"
    temptriple_name = "refers (with name) to the views of"
    temptriple_name_reverse = "has views referred to (with name) by"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonRefersWithoutNameToTheViewsOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "refers (without name) to the views of"
    reverse_name = "has views referred to (without name) by"
    temptriple_name = "refers (without name) to the views of"
    temptriple_name_reverse = "has views referred to (without name) by"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonRequestorOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "requestor of"
    reverse_name = "requested by"
    temptriple_name = "requestor of"
    temptriple_name_reverse = "requested by"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonScribeOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "scribe of"
    reverse_name = "copied/written down by"
    temptriple_name = "scribe of"
    temptriple_name_reverse = "copied/written down by"


class PersonSiblingOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "sibling of"
    reverse_name = "sibling of"
    temptriple_name = "sibling of"
    temptriple_name_reverse = "sibling of"


class PersonSpiritualFriendOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "spiritual friend of"
    reverse_name = "has as spiritual friend"
    temptriple_name = "spiritual friend of"
    temptriple_name_reverse = "has as spiritual friend"


class PersonSponsorOfInstance(TibScholRelationMixin):
    subj_model = Person
    obj_model = Instance
    name = "sponsor of"
    reverse_name = "sponsored by"
    temptriple_name = "sponsor of"
    temptriple_name_reverse = "sponsored by"


class PersonStudentOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "student of"
    reverse_name = "teacher of"
    temptriple_name = "student of"
    temptriple_name_reverse = "teacher of"
    subject_of_teaching = (
        models.CharField(  # TODO: Controlled vocabulary with Work.Subject
            max_length=255,
            blank=True,
            null=True,
            verbose_name="subject of teaching",
        )
    )


class PersonStudiedWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "studied"
    reverse_name = "studied by"
    temptriple_name = "studied"
    temptriple_name_reverse = "studied by"


class PersonTeachesWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "teaches"
    reverse_name = "taught by"
    temptriple_name = "teaches"
    temptriple_name_reverse = "taught by"


class PersonUncleMaternalPaternalOfPerson(TibScholRelationMixin):
    subj_model = Person
    obj_model = Person
    name = "uncle (maternal/paternal) of"
    reverse_name = "nephew (maternal/paternal) of"
    temptriple_name = "uncle (maternal/paternal) of"
    temptriple_name_reverse = "nephew (maternal/paternal) of"


class WorkTaughtAtPlace(TibScholRelationMixin):
    subj_model = Work
    obj_model = Place
    name = "taught at"
    reverse_name = "place of teaching of"


class PersonTranslatorOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "translator of"
    reverse_name = "translated by"


class PersonAnnotatorOfWork(TibScholRelationMixin):
    subj_model = Person
    obj_model = Work
    name = "annotator of"
    reverse_name = "annotated by"
