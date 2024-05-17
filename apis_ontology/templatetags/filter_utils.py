import logging
from apis_ontology.models import ZoteroEntry
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def endswith(value, suffix):
    """Custom filter to check if value ends with the specified suffix."""
    return str(value).endswith(suffix)


@register.filter
def render_links(value):
    if not value:
        return ""

    links = [link.strip() for link in value.split("\n") if link.strip()]
    rendered_links = "<br>".join(
        f'<a href="{link}" target="_blank">{link}</a>' for link in links
    )
    return mark_safe(rendered_links)


@register.filter
def render_list_field(value):
    if not value:
        return ""

    list_vals = [v.strip() for v in value.split("\n") if v.strip()]
    rendered_list = "<br>".join(v for v in list_vals)
    return mark_safe(rendered_list)


@register.filter
def render_coordinate(value):
    try:
        return round(value, 4)
    except:
        return ""


@register.filter
def render_zotero_links(value):
    if not value:
        return ""

    delim = "\n" if "\n" in value else "," if "," in value else ""
    zotero_refs = [
        zotero_id.strip().replace("[", "").replace("]", "")
        for zotero_id in value.split(delim)
        if zotero_id.strip()
    ]
    links = []
    for zotero_id in zotero_refs:
        link_text = zotero_id  # fallback default value
        try:
            zotero_obj = ZoteroEntry.objects.filter(zoteroId=zotero_id)[0]
            link_text = zotero_obj.shortTitle if zotero_obj.shortTitle else zotero_id

        except IndexError:
            logger.error(f"Error finding cached Zotero entry with ID %s", zotero_id)
        except Exception as e:
            logger.error(
                f"Error while fetching zotero data %s\n for %s", repr(e), zotero_id
            )
        links.append(
            f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{link_text}</a>'
        )

    rendered_links = "<br>".join(links)
    return mark_safe(rendered_links)
