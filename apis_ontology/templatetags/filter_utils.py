from django import template

register = template.Library()


@register.filter
def endswith(value, suffix):
    """Custom filter to check if value ends with the specified suffix."""
    return str(value).endswith(suffix)
