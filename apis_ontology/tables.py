import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A

from .templatetags.linkify_list import render_links
from .models import Place


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
