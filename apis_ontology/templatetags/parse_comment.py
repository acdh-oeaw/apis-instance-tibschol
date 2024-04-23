import re

from django import template

register = template.Library()


@register.filter
def parse_comment(value):
    if not value:
        return ""
    print(f"Parsing {value}")

    if "<<" in value and ">>" in value:
        # When comment contains a text to link and a Zotero ID in square bracckets
        pattern = r"<<(.*?) \[(.*?)\]>>"
        subbed = re.sub(
            pattern,
            r'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/\2/item-details#">\1</a>',
            value,
        )
        value = subbed

    if "[" in value and "]" in value:
        # Only Zotero ID without hyperlink text in square brackets
        pattern = r"\[([A-Z0-9]+)\]"
        replacement = r'<a target="_BLANK" href="https://www.zotero.org/groups/4394244/tibschol/items/\1/item-details#">\1</a>'
        subbed = re.sub(pattern, replacement, value)
        value = subbed

    if "(ID:" in value:
        pattern = r"\(ID:\s*(\d+)\)"
        replacement = r'<a target="_BLANK" href="/entity/\1">\1</a>'
        subbed = re.sub(pattern, replacement, value)
        value = subbed

    return value
