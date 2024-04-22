import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A

from .templatetags.linkify_list import render_links, render_list_field
from .models import Person, Place


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
