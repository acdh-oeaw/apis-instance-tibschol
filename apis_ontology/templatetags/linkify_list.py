from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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
