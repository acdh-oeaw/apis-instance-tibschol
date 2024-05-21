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

    title = zotero_info["data"]["title"]
    key = zotero_info["key"]
    creator = zotero_info["data"]["creators"][0]["lastName"]
    constant = "[dPe sgrig 'gan 'khur ba: dByang can lha mo et al.], Chengdu"
    place = zotero_info["data"]["place"]
    publisher = zotero_info["data"]["publisher"]
    date = zotero_info["data"]["date"]
    link = f"""<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{key}/item-details#">{title}</a>"""
    return mark_safe(
        f"""{link}, vol. {object.volume}, {creator} {constant} [{place}]: {publisher}, {date}, pp. {object.pp_kdsb}"""
    )
