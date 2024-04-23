import re

from django import template

register = template.Library()


@register.filter
def parse_comment(value):
    if not value:
        return ""
    print(f"Parsing {value}")

    def replace_zotero_link(match):
        if match.group("text"):
            # Case: <<text [ID]>>
            text = match.group("text")
            zotero_id = match.group("zotero_id")
            return f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{text}</a>'
        elif match.group("zotero_id_only"):
            # Case: [ID]
            zotero_id = match.group("zotero_id_only")
            return f'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/{zotero_id}/item-details#">{zotero_id}</a>'

    def replace_entity_link(match):
        entity_id = match.group("entity_id")
        return f'<a target="_BLANK" href="/entity/{entity_id}">{entity_id}</a>'

    # Combined regex pattern to handle all cases
    combined_pattern = r"<<(?P<text>.*?) \[(?P<zotero_id>[A-Z0-9]+)\]>>|\[(?P<zotero_id_only>[A-Z0-9]+)\]|\(ID:\s*(?P<entity_id>\d+)\)"

    # Apply substitutions using the combined pattern
    transformed_value = re.sub(
        combined_pattern,
        lambda match: replace_zotero_link(match) or replace_entity_link(match),
        value,
    )

    return transformed_value
