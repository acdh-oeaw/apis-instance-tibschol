import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A

from .templatetags.linkify_list import render_links
from .models import Instance, Person, Place, Work


class PlaceTable(AbstractEntityTable):
    class Meta:
        model = Place
        fields = ["id", "label", "latitude", "longitude", "external_links"]
        exclude = ["desc"]

    id = tables.Column(
        linkify=lambda record: record.get_edit_url(),
        empty_values=[],
    )

    def render_external_links(self, value):
        return render_links(value)


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
        linkify=lambda record: record.get_edit_url(),
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
        linkify=lambda record: record.get_edit_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)


class InstanceTable(AbstractEntityTable):
    class Meta:
        model = Instance
        fields = ["id", "tibschol_ref", "name", "author", "external_links"]
        exclude = ["desc"]

    id = tables.Column(
        linkify=lambda record: record.get_edit_url(),
        empty_values=[],
    )
    author = tables.Column(verbose_name="Author", accessor="author", orderable=False)

    def render_external_links(self, value):
        return render_links(value)
