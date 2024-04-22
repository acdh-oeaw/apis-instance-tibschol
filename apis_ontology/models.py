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
    comments = models.TextField(blank=True, null=True)

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


class ZoteroEntry(GenericModel, models.Model):
    zoteroId = models.CharField(max_length=255, verbose_name="Zotero ID")
    shortTitle = models.TextField(blank=True, null=True, verbose_name="Short title")
    fullCitation = models.TextField(blank=True, null=True, verbose_name="Full Citation")
    year = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Year of publication"
    )
