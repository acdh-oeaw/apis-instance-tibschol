import logging
import re


from apis_core.apis_metainfo.models import RootObject
from apis_ontology.models import ZoteroEntry
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from apis_ontology.templatetags.filter_utils import render_list_field

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def render_tei_refs(value):

    def linkify_excerpt_id(xml_id):
        true_id = xml_id.replace('"', "").replace("xml:id=", "").strip().rstrip(".")
        return f"""<a href="#" onclick="showExcerpt('{true_id}'); return false;">
        {true_id}
        </a> """

    if not value.strip():
        return ""
    lines = value.split("\n")
    linked_lines = []
    for line in lines:
        words = line.strip().split()
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

    return "<br />".join(linked_lines) + "<br />" if len(linked_lines) else ""
