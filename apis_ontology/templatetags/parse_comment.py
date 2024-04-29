import logging
import re


from apis_core.apis_metainfo.models import RootObject
from apis_ontology.models import ZoteroEntry
from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def parse_comment(value):
    if not value:
        return ""

    def custom_replace(match):
        if match.group("text"):
            # Handle <<text [ZoteroID]>>
            text = match.group("text")
            zotero_id = match.group("zotero_id")
            replacement = f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{text}</a>'
        elif match.group("zotero_id_only"):
            # Handle [ZoteroID]
            zotero_id = match.group("zotero_id_only")
            try:
                zotero_obj = ZoteroEntry.objects.filter(zoteroId=zotero_id)[0]
                link_text = (
                    zotero_obj.shortTitle if zotero_obj.shortTitle else zotero_id
                )
                return f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{link_text}</a>'
            except Exception as e:
                logger.error(f"Error finding cached Zotero entry with ID %s", zotero_id)
                logger.error(repr(e))
                return f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{zotero_id}</a>'
        elif match.group("entity_id"):
            # Handle (ID: number)
            entity_id = match.group("entity_id")
            try:
                root_obj = RootObject.objects_inheritance.get_subclass(pk=entity_id)
                ct = ContentType.objects.get_for_model(root_obj)
                return f'<a target="_BLANK" href="/apis/apis_ontology.{ct.name}/{root_obj.pk}">{root_obj}</a>'

            except Exception as e:
                logger.error("Error finding entity #%s", entity_id)
                logger.error(repr(e))
                return f'<a target="_BLANK" href="/entity/{entity_id}">{entity_id}</a>'
        else:
            # If no specific group is matched, return the original match
            replacement = match.group(0)

        return replacement

    # Define the regex pattern to capture different groups
    combined_pattern = r"<<(?P<text>.*?) \[(?P<zotero_id>[A-Z0-9]+)\]>>|\[(?P<zotero_id_only>[A-Z0-9]+)\]|\(ID:\s*(?P<entity_id>\d+)\)"

    # Apply substitutions using the combined pattern and custom replacement function
    transformed_value = re.sub(combined_pattern, custom_replace, value)

    return transformed_value
