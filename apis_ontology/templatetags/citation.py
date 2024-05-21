import json
import logging
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

logger = logging.getLogger(__name__)


with open("apis_ontology/static/citations.json", "r") as f:
    citations = json.loads(f.read())


@register.filter
def cite(object):
    print(object.set_num, object.pp_kdsb, object.volume)
    print(citations[object.set_num])
    zotero_info = citations[object.set_num]
    short_title = zotero_info["data"].get("shortTitle", "")
    if not short_title.strip():
        short_title = zotero_info["key"]
    key = zotero_info["key"]
    link = f"""<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{key}/item-details#">{short_title}</a>"""
    return mark_safe(f"""{link}, vol. {object.volume}, {object.pp_kdsb}""")
